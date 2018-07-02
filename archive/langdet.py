# This Python file uses the following encoding: utf-8
from langdetect import detect
import os, sys

lang = detect("يولد جميع الناس أحراراً ومتساوين في الكرامة والحقوق. وهم قد وهبوا العقل والوجدان وعليهم أن يعاملوا بعضهم بعضا بروح الإخاء")

print (lang)


