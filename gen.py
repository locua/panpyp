#!/usr/bin/python3
"""═════════════ Site generator ═════════════╗
║     Python, pandoc static site generator   ║
║                                            ║
╠═════════════════   USE   ══════════════════╬═╼
║
- Run:  `python3 gen.py build` on a ./src directory containing directories of markdown files.
  - keep a ./src/index.md file which will be the home page.
  - and optionally ./src/about.md which will be an about page.
- Build, upload and git upload : `make all`

╠════════════════════ TODO ══════════════════╬═════════╼
║
- make index and about page compilation use template
- only generate edited posts *
- keep track of time edited to avoid this changing when repo is pulled to another machine.
- Neaten and improve efficiency *
- Move to pandoc ... -s, standalone tag,
  to include table of contents.
║
╚════════════════════════════════════════════════════════════════"""
import os, re, time, yaml, sys

""" --- Custom server name and destination directory --- """
server="s"
destdir="/var/www/html"
domain="example.com" # Add the site domain here
rss_description='My virtual scrapbook.'

if os.path.exists('src/config.yml'): # Load yaml config
  with open('src/config.yml','r') as file:
    config_file=yaml.safe_load(file)
    server=config_file['server_name']
    domain=config_file['domain']
    destdir=config_file['destdir']
    
# Globals
pages_list="<div class=\"row\">\n"
rss="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<rss version=\"2.0\">\n\t<channel>\n\t\t<title>"+domain+"</title>\n\t\t<link>https://"+domain+"</link>\n\t\t<description>"+rss_description+"</description>\n\t\t<lastBuildDate>"+time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.localtime())+"</lastBuildDate>\n\t\t<ttl>15</ttl>" # RSS XML channel preamble
m_pattern = r"^[^#~]+.md$"
h_pattern = r"^.+.html$|^.+.txt$"
# t_pattern = r"^.+.txt$"
p = re.compile(m_pattern) # md file regex
hp = re.compile(h_pattern) # html file regex
#tp = re.compile(t_pattern) # txt file regex
posts={} # file list dictionary
foot = "</div><center> <br> <a href=\"#top\">&#x2042; </a><a href=\"/about.html\">⌘</a><br><br></center>\n</body>\n</html>"
tags={}

def get_yaml(f): # parse yaml header from markdown file
  pointer = f.tell()
  if f.readline() != '---\n':
    f.seek(pointer)
    print("\n\n**** Yaml header not detected in ", f.name, "****.\nPLEASE add \n---\nlang: en-GB\ntitle: Title for post\ndescription: Some description\n\n---\nTo the top of the file\n********************")
    sys.exit()
  readline = iter(f.readline, '')
  readline = iter(readline.__next__, '---\n') #underscores needed for Python3?
  return ''.join(readline)

def yaml_rss(fpath,mtime,slug): # get metadata from each page and parse into rss
    global rss
    with open(fpath, encoding='UTF-8') as f:
        config = list(yaml.load_all(get_yaml(f), Loader=yaml.SafeLoader))
        text = f.read()
        if 'title' in config[0]: # Add items to rss feed
            rss+="\n\t\t<item>\n\t\t\t<title>"+config[0]["title"]+"</title>"
            if 'description' in config[0]:
                rss+="\n\t\t\t<description>"+config[0]["description"]+"</description>"
            else:
                rss+="\n\t\t\t<description>None</description>"
            rss+="\n\t\t\t<link>"+slug+"</link>\n\t\t\t<guid isPermaLink=\"false\">"+slug+"</guid>\n\t\t\t<pubDate>"+mtime+"</pubDate>\n\t\t</item>"

def create_post(file_abs, name, category): # compile markdown post to html page
    pst=time.time()
    rfc_822_time = time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.localtime(os.path.getmtime(file_abs)))
    slug = "https://"+domain+category+name+".html"
    yaml_rss(file_abs, rfc_822_time,slug)
    _time="<p>Last edited :- "+rfc_822_time+"</p><br>"
    script="pandoc -f markdown -t html -s --toc --toc-depth=3 --template=templates/pream.html --mathml -V time='"+_time+"' "+file_abs+" > "+" ./site"+category+name+".html.tmp"
    os.system(script)
    content = open("site"+category+name+".html.tmp", "r").read() # write to index.html
    page = open("site"+category+name+".html", "w", encoding="utf-8")
    _title = ""
    description = ""
    meta = ""
    with open(file_abs, encoding='UTF-8') as f:
        meta = list(yaml.load_all(get_yaml(f), Loader=yaml.SafeLoader))[0]
        _title = meta["title"]
        if 'description' in meta:
            description = meta["description"]
        if 'tags' in meta: # extract tags and store
          if len(meta["tags"])>0:
            for t in meta["tags"]:
              if t not in tags.keys():
                tags[t]=[]
              tags[t].append(file_abs)

    page.write(content) # Write index to index.html
    page.close()
    os.remove("site"+category+name+".html.tmp")
    print("[Created page (in "+str(round(time.time()-pst, 2))+" s): "+category+name+".html"+"]")

def gen_tags(): # Generate html for tags and tag pages
  if not tags:
    return ""
  tagels="\n<center>"
  os.system("mkdir ./site/t")
  for i,k in enumerate(tags.keys()):
    links="<h2>Pages tagged <i>"+k+"</i></h2>\n<ul>"
    for link in tags[k]:
      l=link.replace("./src", "").split(".md")[0]
      links+="\n<li><a href=\""+l+".html\">"+l+"</a></li>"
    links+="\n</ul>\n"
    if i==0:
      tagels+="<a href=\"/t/"+k+".html\">"+k+"</a>&nbsp;"
    else:
      tagels+="∩&nbsp;<a href=\"/t/"+k+".html\">"+k+"</a>&nbsp;"
    tagpage = open("./site/t/"+k+".html", "w")
    preampage = open("templates/tags_pream.html","r").read()
    tagpage.write(preampage+links+"</body>\n</html>")
    tagpage.close()
  tagels+="</center>"
  return tagels

def main(): # Main function. Generates site directory with rss feed page files and index.
  global pages_list
  global rss
  print("[...Starting HTML...]")
  start=time.time()
  # Grab files in directories
  root_files = []
  for root, dirs, files, in os.walk("./src"):
      if root=="./src":
        root_files.append(files) # add files in root too
      for d in dirs:
          for files in os.walk("./src/" +d):
              posts[d]=files

  categories = list(posts.keys())
  if os.path.exists('site'):
      os.system("rm -r site/* && mkdir ./site/assets")
  else:
      os.system("mkdir -p ./site/assets")

  os.system("cp gen.py site/assets/ && cp -r assets/* site/assets") # copy this script and styles to assets

  num_cats=len(categories)
  for i,cat in enumerate(categories):# Generate index pages_list and categories. Compile each post.
      os.system('mkdir site/'+cat)
      if i%2==0 and i!=0:
        # pages_list+="</div>\n<div>"
        pages_list+="<div class=\"w-100 d-none d-md-block\"></div>\n"

      pages_list+="<div class=\"col-6 col-sm-6\"><h2>"+cat.capitalize().replace("_"," ")+"</h2>\n<ul>\n" # category header
      for f in posts[cat][2]:
          if p.findall(f): # check if markdown file
              title = f.split(".", 1)[0] # remove extension
              absf = posts[cat][0]+"/"+f # file position absolute
              create_post(absf,title,"/"+cat+"/") # create html post from md
              pages_list+="<li><a href=\""+"/"+cat+"/"+title+".html\">"+title.capitalize().replace("_", " ")+"</a></li>\n" # index category list
          elif hp.findall(f): # if html or txt file copy it
                  title = f.split(".", 1)[0] # remove extension
                  pages_list+="<li><a href=\""+"/"+cat+"/"+title+"."+f.split(".",1)[1]+"\">"+title.capitalize().replace("_", " ")+"</a></li>\n" # index category list
                  print("[Copied page "+f+"]")
                  os.system("cp src/"+cat+"/"+f+" site/"+cat+"/")
                  continue
          #os.system("cp src/"+cat+"/"+f+" site/assets/")
      pages_list+="</ul></div>\n"


  root_files[0].remove("index.md") # Create pages for root markdown files.
  for f in root_files[0]:
    if p.findall(f):
      create_post("./src/"+f, f.split(".")[0], "/")

  rss+="\n\t</channel>\n</rss>" # RSS foot
  tagels = gen_tags()

  # Compile index and create add post category lists
  os.system('pandoc --verbose -s -f markdown -t html -V tag_list="'+tagels+'" --template=templates/index_pream.html src/index.md > tmp.html')
  pages_list+="</div></div>\n<br><br>"
  index=open("tmp.html").read() + pages_list + "<center><a href=\"#top\">&#x2042;</a> <a href=\"/about.html\">⌘</a></center>\n<br>\n<br>\n</body>\n</html>" # add index.md stuff
  os.remove("tmp.html") # delete tmp.html
  index_file = open("site/index.html", "w", encoding="utf-8") # write to index.html
  print("[Compiled HTML in ",round(time.time()-start, 3),"seconds."+"]")
  start=time.time()
  print("[Writing RSS"+"]")
  rss_file = open("site/rss.xml", "w", encoding="utf-8") # write to index.html
  index_file.write(index) # Write index to index.html
  rss_file.write(rss) # Write rss feed to rss file
  index_file.close()
  rss_file.close()
  print("[Compiled RSS in ",round(time.time()-start, 3),"seconds"+"]"+"\nEND")

if __name__ == "__main__":
  if len(sys.argv)<2:
    print("\nNo arguments.\n\n Please try:\n 'git',\n 'build',\n 'serve' ,\n 'all',\n 'upload' (for this option make sure there is an ssh server called 's' available.\n\t\tThe destination directory is /var/www/html by default.\n\t\tSet server and destdir variables in generate.py file.)")
    sys.exit()
  elif (sys.argv[1]=="build"):
    print("[Building site."+"]")
    main()
  elif (sys.argv[1]=="upload"):
    print("[Uploading files."+"]")
    os.system("rsync -rh  --info=progress2 --exclude='*.swp' site/* root@"+server+":"+destdir+" --delete")
  elif (sys.argv[1]=="all"):
    print("[Building..."+"]")
    main()
    print("[Uploading..."+"]")
    os.system("rsync -rh  --info=progress2 --exclude='*.swp' site/* root@"+server+":"+destdir+" --delete")
    print("[Git commit and push..."+"]")
    os.system("git commit -am \"post\" && git push")
  elif (sys.argv[1]=="serve"):
    os.system("cd site && python3 -m http.server")
  elif (sys.argv[1]=="git"):
    print("[Commiting and pushing latest to git."+"]")
    os.system("git commit -am \"post\" && git push")
  else:
    print("\nArgument is invalid\n")
    print("Please try:\n 'git',\n 'build',\n 'serve' ,\n 'all',\n 'upload' (for this option make sure there is an ssh server called 's' available.\n\t\tThe destination directory is /var/www/html by default.\n\t\tSet server and destdir variables in generate.py file.)")
    sys.exit()

