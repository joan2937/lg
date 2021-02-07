#!/usr/bin/env python3

import sys

lgpio_m1="""
.\\" Process this file with
.\\" groff -man -Tascii lg.3
.\\"
.TH lgpio 3 2020-2021 Linux "lg archive"
.SH NAME
lgpio - A C library to manipulate a local SBC's GPIO.\n
.SH SYNOPSIS\n
#include <lgpio.h>\n

gcc -Wall -o prog prog.c -llgpio\n
\&./prog
.SH DESCRIPTION\n
"""

rgpio_m1="""
.\\" Process this file with
.\\" groff -man -Tascii lgd_if.3
.\\"
.TH rgpio 3 2020-2021 Linux "lg archive"
.SH NAME
rgpio - A C library to manipulate a remote SBC's GPIO.\n
.SH SYNOPSIS\n
#include <rgpio.h>\n

gcc -Wall -o prog prog.c -lrgpio\n
\&./prog
.SH DESCRIPTION\n
"""

lgpio_m2="""
.SH SEE ALSO\n
rgpiod(1), rgs(1), rgpio(3)
"""

rgpio_m2="""
.SH SEE ALSO\n
rgpiod(1), rgs(1), lgpio(3)
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

NONE    =0
MAN     =1
TEXT    =2
OVERVIEW=4
FUNC    =5
DESC    =6
OPT     =7
PARAMS  =8
DEFS    =9

param_used = []
param_defd = []
param_refd = []

at = NONE

in_code = False
in_pard = False
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
   if obj == "lgpio":
      emit(lgpio_m1)
   elif obj == "rgpio":
      emit(rgpio_m1)

   emit("\n.ad l\n")
   emit("\n.nh\n")

while True:

   line = get_line(f)

   if line == "":
      for p in param_used:
         if p not in param_defd:
            sys.stderr.write("{} used but not defined.\n".format(p))
      for p in param_defd:
         if p not in param_used and p not in param_refd:
            sys.stderr.write("{} defined but not used.\n".format(p))
      break

   while line.find("[*") != -1 and line.find("*]") != -1:
      (b, s, e) = line.partition("[*")
      (l, s, e) = e.partition("*]")

      if man:
         line = "{}\\fB{}\\fP{}".format(b, l, e)
      else:
         line = "{}<a href=\"#{}\">{}</a>{}".format(b, l, l, e)

      if l not in param_refd:
         param_refd.append(l)

   while line.find("[[") != -1 and line.find("]]") != -1:
      (b, s, e) = line.partition("[[")
      (l, s, e) = e.partition("]]")

      if man:
         line = "{}\\fB{}\\fP{}".format(b, l, e)
      else:
         line = "{}<a href=\"{}\">{}</a>{}".format(b, l, l, e)

   while line.find("[+") != -1 and line.find("+]") != -1:
      (b, s, e) = line.partition("[+")
      (l, s, e) = e.partition("+]")

      if man:
         line = "{}\\fB{}\\fP{}".format(b, l, e)
      else:
         line = "{}<a href=\"{}.html\">{}</a>{}".format(b, l.lower(), l, e)

   if line[0] == '*' and line[-2] == '*':
      if man:
         line = ".SS {}".format(line[1:-2])
      else:
         line = "<h3>{}</h3>".format(line[1:-2])

   if line.startswith("o "):
      if not in_list:
         in_list = True
         if not man:
            emit("<ul>")
      if man:
         emit("\n.br\n"+line)
      else:
         emit("<li>"+ line[2:] +"</li>")
      continue

   if in_list:
      in_list = False
      if not man:
         emit("</ul>")

   if line == "/*MAN\n":
      at = MAN
      continue

   elif line == "MAN*/\n":
      at = NONE
      continue

   if line == "/*TEXT\n":
      at = TEXT
      continue

   elif line == "TEXT*/\n":
      at = NONE
      continue

   elif line == "/*OVERVIEW\n":

      if man:
         emit("\n.SH OVERVIEW\n")
      else:
         emit("<h2>OVERVIEW</h2>")
         emit(
            "<table border=\"0\" cellpadding=\"2\" cellspacing=\"2\"><tbody>")

      at = OVERVIEW
      continue

   elif line == "OVERVIEW*/\n":

      if man:
         emit(".SH FUNCTIONS\n")
      else:
         emit("</tbody></table>")
         emit("<h2>FUNCTIONS</h2>")

      at = NONE

   elif line == "/*F*/\n":
      in_code = False
      func_def=""
      line = get_line(f)
      at = FUNC

   elif line == "/*D\n":

      # Function definition should be complete.  Normalise definition

      func_def = func_def.replace("\n", " ")

      while func_def.find("  ") != -1:
         func_def = func_def.replace("  ", " ")

      func_def = func_def.replace("( ", "(")
      func_def = func_def.replace(" (", "(")

      (rf, sep1, end1) = func_def.partition("(")
      (parl, sep2, end2) = end1.partition(")")
      tps = parl.split(",")
      rf = rf.split(" ")

      if len(rf) > 2: # const
         const = rf[0]+" "
         ret = rf[1]
         func = rf[2]
      else:
         const = ""
         ret = rf[0]
         func = rf[1]

      if ret not in param_used:
         param_used.append(ret)

      if man:
         t = "\\fB" + const + ret + " " + func + "(" + parl + ")\\fP"
         emit("\n.IP \"{}\"\n.IP \"\" 4\n".format(t))
      else:
         emit("<h3><a name=\"{}\"></a><a href=\"#{}\"><small>{}</small></a> {}".
            format(nostar(func), ret, const + ret, func))
         emit("<small>(")

      x = 0
      for tp in tps:
         tp = tp.strip()
         tp = tp.split()

         if len(tp) < 2:
            t=tp[0]
            p=""
         elif len(tp) == 2:
            t = tp[0]
            tf = tp[0]
            p = tp[1]
         else:
            t = tp[-2]
            tf = tp[-3] + " "+ tp[-2]
            p = tp[-1]

         if p != "":
            if p not in param_used:
               param_used.append(p)
            if t not in param_used:
               param_used.append(t)
            if x > 0:

               if man:
                  pass
               else:
                  emit(", ")

            x += 1

            if man:
               pass
            else:

               emit("<a href=\"#{}\">{}</a> <a href=\"#{}\">{}</a>".
                  format(t, tf, p, p))

         else:

            if man:
               pass
            else:
               emit("{}".format(t))

      if man:
         pass
      else:
         emit(")</small></h3>\n")

      line = get_line(f)
      at = DESC

   elif line == "D*/\n":
      at = NONE

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

   elif line == "/*PARAMS\n":
      last_par = "*"

      if man:
         emit(".SH PARAMETERS\n")
      else:
         emit("<h2>PARAMETERS</h2>")

      at = PARAMS
      continue

   elif line == "PARAMS*/\n":
      at = NONE

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


   if at != NONE and at != OVERVIEW:
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
            line = line.replace("<a&nbsp;href", "<a href")
            line = line.replace("\n", "<br>")

   if at == TEXT:
      emit(line)

   elif at == OVERVIEW:
      if line == "\n":

         if man:
            emit("\n.br\n")
         else:
            emit("<tr><td></td><td></td></tr>")

      else:
         (func, sep, desc) = line.partition(" ")
         if desc != "":

            if man:
               emit("\n.br\n{}".format(line.strip()))
            else:
               emit("<tr><td><a href=\"#{}\">{}</a></td><td>{}</td></tr>".
                  format(func, func, desc))

         else:

            if man:
               emit(".SS {}".format(line.replace("_", " ").strip()))
            else:
               emit("<tr><td><b>{}</b></td><td></td></tr>".
                  format(func.replace("_", " ")))

   elif at == FUNC:
      func_def += line

   elif at == DESC:
      emit(line)

   elif at == PARAMS:
      if line.find("::") != -1:
         (par, sep, end) = line.partition("::")
         par = par.strip()
         end = end.strip()

         if nostar(par.lower()) < nostar(last_par.lower()):
            sys.stderr.write("Out of order {} after {}.\n".
               format(par, last_par))
         last_par = par

         if par in param_defd:
            sys.stderr.write("Duplicate definition of {}.\n".format(par))
         else:
            param_defd.append(par)

         if end != "":
            end = ": " + end
         if man:
            emit("\n.IP \"\\fB{}\\fP{}\" 0\n".format(par, end))
         else:
            emit("<h4><a name=\"{}\">{}</a>{}</h4>".format(par, par, end))

      else:
         emit(line)

   elif at == MAN:
      if man:
         emit(line)

   elif at == OPT:
      line = line.split("|")
      if man:
         emit("\n.IP \"\\fB{}\\fP\"\n{}.\n{}.\n{}.".format(
         line[0], line[1], line[2], line[3]))
      else:
         emit("<tr><td><b>{}</b></td><td>{}</td><td>{}</td><td>{}</td></tr>".
            format(line[0], line[1], line[2], line[3]))

   elif at == DEFS:
      line = line.replace("#define ", "")
      line = line.replace("#define&nbsp;", "")
      emit(line)

if man:
   if obj == "lgpio":
      emit(lgpio_m2)
   elif obj == "rgpio":
      emit(rgpio_m2)


f.close()

