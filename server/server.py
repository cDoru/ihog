from bottle import route, run, request, static_file, redirect
import random
import Image
import os
import urllib2

@route('/')
@route('/index')
def index():
    resp = "<html><head><title>HOG Glasses</title></head>"

    if request.query.embed:
        resp = resp + """<body style="background-color:#fff;font-family:Arial;padding:0;margin:0;"><div style="width:400px;">"""
    else:
        resp = resp + """<body style="background-color:#EFEFEF;font-family:Arial;padding:0;margin:0;"><div style="width:400px;padding:25px;margin:50px auto; background-color:#fff;"><h1>HOG Glasses</h1>"""

    resp = resp + """
<script>
function go(url) {
document.getElementById("url").value = url;
document.forms["form"].submit();
}
</script>
<style>
img { cursor : pointer; }
</style>
<p>How do computers see the world? Upload a photo, and we'll
show you!</p>
<form target="_parent" action="/process" id="form" method="post" enctype="multipart/form-data">
<table><tr>
<td><strong>Upload:</strong></td><td><input type="file" name="data"></td>
<td><input type="submit" value="Process"></td>
</tr><td>&nbsp;</td></tr><tr>
<td></td><td>or</td></tr>
<tr><td>&nbsp;</td></tr><tr>
<td><strong>URL:</strong></td>
<td><input type="text" id="url" name="url" style="width:250px;" value="http://"></td>
<td><input type="submit" value="Process"></td>
</tr>
<tr><td>&nbsp;</td></tr><tr>
<tr>
<td></td><td>or</td>
</tr>
<tr><td>&nbsp;</td></tr><tr>
<td><strong>Click One:</strong> </td>
<td colspan="2">
<img src="http://www.brynosaurus.com/img/dscn5239.jpg" height="45" onclick="go(this.src);">
<img src="http://www.cs.ubc.ca/~murphyk/Vision/placeRecognition_files/antonio_helmet.jpg" height="45" onclick="go(this.src);">
<img src="http://web.mit.edu/jessiehl/Public/cannonhack2.jpg" height="45" onclick="go(this.src);">
<img src="http://familyofficesgroup.com/wp-content/uploads/2012/02/Boston_Ma.jpg" height="45" onclick="go(this.src);">
<img src="http://cloudfront2.bostinno.com/wp-content/uploads/2012/10/Campus-Police-Car-on-the-Great-Dome.jpeg" height="45" onclick="go(this.src);">
</td>
</tr>
</table>
</form>
"""
    if not request.query.embed:
        resp = resp + "<p>Wondering how this works? <a href='http://mit.edu/vondrick/ihog'>Learn more &raquo;</a></p>"

    resp = resp + """
</div>
</body>
</html>"""
    return resp

@route('/process', method='POST')
def process():
    buffersize = 1024 * 1024
    maxfilesize = 1024 * 1024 * 100
    data = request.files.data
    datafile = None
    if data and data.file:
        datafile = data.file
    elif not data and request.forms.url:
        datafile = urllib2.urlopen(request.forms.url)
    if datafile:
        id = random.randint(0, 999999999999)
        print id
        with open("/scratch/hallucination-daemon/staging/{0}".format(id), "w") as f:
            buffer = datafile.read(buffersize)
            f.write(buffer)
            bytesread = buffersize
            while buffer != "":
                buffer = datafile.read(buffersize)
                f.write(buffer)
                bytesread += buffersize
                if bytesread > maxfilesize:
                    return "File is too big."
        try:
            image = Image.open("/scratch/hallucination-daemon/staging/{0}".format(id))        
        except:
            return "File does not appear to be an image."
        image.convert("RGB").save("/scratch/hallucination-daemon/images/{0}.jpg".format(id))

        redirect("/wait/{0}".format(id))
    else:
        return "You did not upload a file."

@route('/wait/<id>')
def wait(id):
    if os.path.exists("/scratch/hallucination-daemon/out/original-{0}.jpg".format(id)):
        redirect("/show/{0}".format(id))
    else:
        return "<html><head><title>Processing...</title></head><body><div style='margin-top : 50px; text-align:center;'>One second please...</div><script>window.setTimeout(function() {{ window.location.reload(); }}, 500);</script></body></html>".format(id)
    

@route('/show/<id>')
def show(id):
    resp = """<html><head><title>HOG Glasses</title></head>
<body style="font-family:Arial;">
<div style="margin:20px auto; width:550px;">
<h1>HOG Glasses</h1>
<p>The left shows the image you uploaded. The right shows how a computer sees the same photo. Notice how shadows are removed, fine details are lost, and the image is more noisey. The bottom shows a standard visualiation that researchers analyze. <a href="/">Upload another image &raquo;</a></p>
</div>
<table style="margin:0 auto;"><tr><th>What You See</th><th>What Computers See</th></tr><tr><td style="padding:0 20px;">
<img src="/getimage/original-{0}">
</td>
<td style="padding:0 20px;">
<img src="/getimage/ihog-{0}">
</td>
</tr>
<tr>
<th colspan="2" style="padding-top:50px;">What Researchers See</th>
</tr>
<tr>
<td style="text-align:center;"colspan="2"><img src="/getimage/glyph-{0}"></td>
</tr>
</table>
</body>
</html>""".format(id)
    return resp

@route('/getimage/<id>')
def getimage(id):
    return static_file("{0}.jpg".format(id), root="/scratch/hallucination-daemon/out")

import socket
run(host="{0}.csail.mit.edu".format(socket.gethostname()), port=8080)