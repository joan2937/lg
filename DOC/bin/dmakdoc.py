#!/usr/bin/env python3

import sys

rgpiod_m1="""
.\" Process this file with
.\" groff -man -Tascii lgd.1
.\"
.TH rgpiod 1 2020-2021 Linux "lg archive"
.SH NAME
rgpiod - a daemon to allow remote access to a SBC's GPIO.\n
.SH SYNOPSIS\n
rgpiod [OPTION]...&
.SH DESCRIPTION\n
"""

rgpiod_m2="""
.SH SEE ALSO\n
rgs(1), lgpio(3), rgpio(3)
"""

def error(s):
   sys.stderr.write(s)

def emit(s):
   sys.stdout.write(s)

def get_line(f):
   line = f.readline()
   if man:
      line = line.replace(" \n", "\n.br\n")
   else:
      line = line.replace("<", "&lt;")
      line = line.replace(">", "&gt;")
      line = line.replace(" \n", "<br>\n")
   return line

def nostar(k):
   if k[0] == "*":
      return k[1:]
   else:
      return k

NONE=0
MAN=1
TEXT=2
OPT=3
DEFS=4

at = NONE

in_code = False
in_table = False
in_list = False

if len(sys.argv) > 2:
   obj = sys.argv[1]
   fn = sys.argv[2]
   if len(sys.argv) > 3:
      man = True
   else:
      man = False
else:
   exit("bad args, need page file [man]")
try:
   f = open(fn, "r")
except:
   exit("aborting, can't open {}".format(fn))

if man:
   if obj == "rgpiod":
      emit(rgpiod_m1)

   emit("\n.ad l\n")
   emit("\n.nh\n")

while True:

   line = get_line(f)

   if line == "":
      break

   while line.find("[*") != -1 and line.find("*]") != -1:
      (b, s, e) = line.partition("[*")
      (l, s, e) = e.partition("*]")

      if man:
         line = "{}\\fB{}\\fP{}".format(b, l, e)
      else:
         line = "{}<a href=\"#{}\">{}</a>{}".format(b, l, l, e)

   while line.find("[+") != -1 and line.find("+]") != -1:
      (b, s, e) = line.partition("[+")
      (l, s, e) = e.partition("+]")

      if man:
         line = "{}\\fB{}\\fP{}".format(b, l, e)
      else:
         line = "{}<a href=\"{}.html\">{}</a>{}".format(b, l.lower(), l, e)

   while line.find("[#") != -1 and line.find("#]") != -1:
      (b, s, e) = line.partition("[#")
      (l, s, e) = e.partition("#]")

      if man:
         line = "{}\\fB{}\\fP{}".format(b, l, e)
      else:
         line = "{}<b>{}</b>{}".format(b, l, e)

   if line[0] == '*' and line[-2] == '*':
      if man:
         line = ".SS {}".format(line[1:-2])
      else:
         line = "<h3>{}</h3>".format(line[1:-2])

   if line[0] == '^' and line[-2] == '^':
      if man:
         line = ".SS {}".format(line[1:-2])
      else:
         line = "<br><b>{}</b><br>".format(line[1:-2])

   if line == "/*MAN\n":
      at = MAN
      continue

   elif line == "MAN*/\n":
      at = NONE
      continue

   if line.startswith("/*TEXT "):
      title = line[7:-1]
      if man:
         emit("\n.SH {}\n".format(title))
      else:
         emit("<h2><a name=\"{}\">{}</a></h2>".format(title, title))
      at = TEXT
      continue
   elif line == "/*TEXT\n":
      at = TEXT
      continue


   elif line == "TEXT*/\n":
      at = NONE
      continue

   elif line == "/*O\n":
      if man:
         emit(".SH OPTIONS\n")
      else:
         emit("<table border=\"1\" cellpadding=\"2\" cellspacing=\"2\"><tbody>")
      at = OPT
      continue

   elif line == "O*/\n":
      if man:
         pass
      else:
         emit("</tbody></table>")
      at = NONE
      continue

   elif line.startswith("/*DEF_S "):
      title = line[8:-3]
      in_code = True
      if man:
         emit(".SH {}\n".format(title))
         emit("\n.EX\n")
      else:
         emit("<h2>{}</h2>".format(title))
         emit("<code>")
      at = DEFS
      continue

   elif line == "/*DEF_E*/\n":
      in_code = False
      if man:
        emit("\n.EE\n")
      else:
         emit("</code>")
      at = NONE
      continue

   elif line == "[ol]\n":
      if in_list:
         in_list = False
         if man:
            pass
         else:
            emit("</ol>")
      else:
         in_list = True
         if man:
            pass
         else:
            emit("<ol>")
      continue

   elif line == "[ul]\n":
      if in_list:
         in_list = False
         if man:
            pass
         else:
            emit("</ul>")
      else:
         in_list = True
         if man:
            pass
         else:
            emit("<ul>")
      continue

   if at != NONE:
      if in_list:
         if man:
            emit(".br\no "+line)
         else:
            emit("<li>"+line+"</li>")
         continue

      if line.find("@") != -1:
         if not in_table:
            in_table = True

            if man:
               pass
            else:
               emit("<table border=\"1\" cellpadding=\"2\" cellspacing=\"2\"><tbody>")

         if man:
            line = line.replace("@", " ")
            emit(line)
            # emit("\n.br\n")
            emit(".br\n")
         else:
            emit("<tr>")
            cols = line.split("@")
            for col in cols:
               emit("<td>{}</td>".format(col.strip()))
            emit("</tr>")

         continue

      else:
         if in_table:
            in_table = False

            if man:
               pass
            else:
               emit("</tbody></table>")

      if line == "...\n" or line == ". .\n":
         if in_code:
            in_code = False

            if man:
               emit("\n.EE\n")
            else:
               emit("</code>")

         else:
            in_code = True
            if line == "...\n":

               if man:
                  emit("\\fBExample\\fP\n.br\n")
               else:
                  emit("<b><small>Example</small></b><br><br>")

            if man:
               emit("\n.EX\n")
            else:
               emit("<code>")

         continue

      if line == "\n":

         if man:
            emit("\n.br\n")
         else:
            emit("<br>")

         if not in_code:
            if man:
              emit("\n.br\n")
            else:
               emit("<br>")

         continue


      if in_code:

         if man:
            line = line.replace("\n", "\n.br\n")
         else:
            line = line.replace(" ", "&nbsp;")
            line = line.replace("\n", "<br>")

   if at == TEXT:
      emit(line)

   elif at == MAN:
      if man:
         emit(line)

   elif at == OPT:
      line = line.split("|")
      if man:
         emit("\n.IP \"\\fB{}\\fP\"\n{}.".format(line[0], line[1]))
      else:
         emit("<tr><td><b>{}</b></td><td>{}</td></tr>".
            format(line[0], line[1]))

   elif at == DEFS:
      line = line.replace("#define ", "")
      line = line.replace("#define&nbsp;", "")
      emit(line)

if man:
   if obj == "rgpiod":
      emit(rgpiod_m2)

f.close()

