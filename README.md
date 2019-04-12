# waterjug
<h2>Water Jug problem</h2>
cd into your virtualenv folder and create a virtualenv (alternatively you can use pipenv if you have it installed):
<pre>
python3 -m virtualenv flaskapp
</pre>
Activate the virtualenv
<pre>
source $venv/flaskapp/bin/activate
</pre>
Check out the repo </br>
Go into the waterjug folder and install the requirements
<pre>
cd waterjug
pip install -r requirements
</pre>
Fire it up!
<pre>
python waterjug.py
</pre>
Point your browser to http://localhost:5847
<h2>Tests</h2>
There is a small BASH script that checks for basic functionality. In a terminal, cd into the waterjug folder, and run:
<pre>
./jugtests
</pre>
<br>

