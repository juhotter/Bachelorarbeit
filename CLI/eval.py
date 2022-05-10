#!/usr/local/bin/python3
from cmath import nan
from datetime import date
from email.policy import default
from itertools import count, groupby
from pydoc import visiblename
from sre_constants import SUCCESS
from tokenize import group
import click
import subprocess
import json
import pandas
import matplotlib.pyplot as plt
import time
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator)



proc = None
model = "noModell"
start = None



def parseTextFile(textname):
    datei = open(textname,'r')
    lines = datei.readlines()
    for i in lines:
        click.echo(i.strip())
        subprocess.call("apkeep -a "+i.strip()+" .", shell=True )
    datei.close()



def adb_install(apkfile):
    subprocess.run("adb devices", shell=True)
    subprocess.run("adb install "+apkfile,shell=True)
    

def adb_run(apkfile):
    packagename = apkfile[:len(apkfile)-4]
    click.echo(packagename)
    subprocess.run("adb shell monkey -p "+packagename+" -c android.intent.category.LAUNCHER 1  ",shell=True) 
    subprocess.run("adb push  monkey.sh /data/local/tmp/monkey.sh",shell = True)
    subprocess.run("adb shell chmod +x /data/local/tmp/monkey.sh",shell = True)
    global start
    start = time.time()
    subprocess.run("adb shell /data/local/tmp/monkey.sh", shell = True)

def adb_uninstall_after_time(apkfile):
    packagename = apkfile[:len(apkfile)-4]
    subprocess.run("adb uninstall "+packagename,shell=True)
    global start
    time.sleep(max(0, start - time.time() + 30))


def startMitmProxy(appname,method):
    
    global proc 
    newappname = appname[:len(appname)-4]
    #change TLS_device and Downloadgroup if you need it for grouping
    proc = subprocess.Popen("mitmdump -s tlslogger.py --set tls_logfile=tls-log.txt --set tls_app="+newappname+" --set tls_method="+method+" --set tls_device=ONEPLUS_A6003 --set tls_downloadgroup=mehr_als_1_Milliarde",shell=True)

def endMitmProxy():
    click.echo("Mitmproxy closes..")
    global proc
    proc.terminate()



def parseJsonFile_emulator_vs_hardware():
    global model
    model = "Oneplus 6 - Android 11 "
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    dataframe['device'] = dataframe['device'].replace(["ONEPLUS_A6003"],'Hardware\nGerät')
    dataframe['device'] = dataframe['device'].replace(["Emulator_11"],'Emuliertes\nGerät')

    grouped = dataframe.groupby('device')["success"].value_counts().unstack().sort_values([True],ascending=True).apply(lambda x: x/x.sum()*100, axis=1)
    print(grouped)
    
    ax = grouped.plot.barh(stacked=True,color=['slategray', 'powderblue'])
    ax.set_xlabel('Contacted-Domains')
    ax.set_ylabel('')
 
    for container in ax.containers:
        ax.bar_label(container,label_type='center',fmt='%.1f%%', fontsize=6)
    
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    ax.plot()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d%%'))
    ax.figure.savefig('emulator_vs_hardware.pdf',bbox_inches='tight')
    plt.show()



def parseJsonFile_gruppenvergleich():
    global model
    model = "Oneplus 6 - Android 11 "
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    dataframe['group'] = dataframe['group'].replace(["Weniger_1000"],'< 1k')
    dataframe['group'] = dataframe['group'].replace(["Million_bis_Milliarde"],'1Md - 1M')
    dataframe['group'] = dataframe['group'].replace(["mehr_als_1_Milliarde"],'> 1Md')
    dataframe['group'] = dataframe['group'].replace(["Thousand_to_Million"],'1M - 1k')
    
    new_group = dataframe.groupby("app",)["group","success"].value_counts().unstack()
    grouped= new_group.groupby("group").mean().apply(lambda x: x/x.sum()*100, axis=1).sort_values([True],ascending=False)
    
    ax = grouped.plot.barh(stacked=True,color=['slategray', 'powderblue'])
    for container in ax.containers:
        ax.bar_label(container,label_type='center',fmt='%.1f%%', fontsize=6)
        
    ax.set_xlabel('Contacted-Domains')
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d%%'))
    ax.legend(["nicht entschlüsselte Verbindungen", "entschlüsselte Verbindungen"],bbox_to_anchor=(0,1), loc="lower left")
    ax.plot()
    ax.figure.savefig('gruppenvergleich.pdf',bbox_inches='tight')
    plt.show()


def parseJsonFile_interaktionenvergleich():
    global model
    model = "Oneplus 6 - Android 11 "
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    print(dataframe.groupby("version")["success"].value_counts())
    dataframe['version'] = dataframe['version'].replace([1],'keine\nInteraktion')
    dataframe['version'] = dataframe['version'].replace([2],'manuelle\nInteraktion')
    dataframe['version'] = dataframe['version'].replace([3],'automatisierte\nInteraktion')
    grouped = dataframe.groupby('version')["success"].value_counts().unstack().sort_values([True],ascending=True)
    ax = grouped.plot.barh(stacked=True,color=['slategray', 'powderblue'])
    ax.set_xlabel('Contacted-Domains')
    ax.set_ylabel("")
    ax.plot()
    ax.figure.savefig('vergleich.pdf',bbox_inches='tight')
    plt.show()
   

def parseJsonFile_einzelneApps(): 
    global model
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    all_app_names = sorted(dataframe['app'].unique())
    grouped = dataframe.groupby('app')["success"].value_counts().unstack().apply(lambda x: x/x.sum()*100, axis=1).sort_values([True],ascending=False)
    print(grouped)
    ax = grouped.plot.barh(stacked=True,color=['slategray', 'powderblue'])
    for p in ax.patches:
        left, bottom, width, height = p.get_bbox().bounds
        if width != 0.0:
         ax.annotate(("%.1f%%") %(width), xy=(left+width/2, bottom+height/2), 
                    ha='center', va='center', fontsize=5)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d%%'))
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    ax.set_xlabel('Contacted-Domains')
    ax.set_ylabel('')
    ax.plot()
    ax.figure.savefig('all_apps_listed_rooted.pdf',bbox_inches='tight')
    plt.show()
 
def parseJsonFile_failure_apps():
    df = pandas.DataFrame({
    'Objection': [14,8,5,3],
    'Frida': [10,2,2,0],
    'Apkmitm': [11,3,0,1],
    'Emulator': [12,5,2,1],
    },
    index=["> 1Md","1M - 1Md","1k - 1M","< 1k"])
    df.sort_index()
    ax = df.plot.barh(stacked=True,color=['lightgrey', 'powderblue','wheat','plum'],)
    for p in ax.patches:
        left, bottom, width, height = p.get_bbox().bounds
        if width != 0.0:
         ax.annotate(("%d%%") %(width), xy=(left+width/2, bottom+height/2), 
                    ha='center', va='center', fontsize=4)
    ax.set_xlabel("Prozentualer Anteil an fehlgeschlagenen Apps")
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d%%'))
    ax.plot()
    ax.figure.savefig('fehlschlag.pdf',bbox_inches='tight')
    plt.show()
    
    
def parseJsonFile_vergleich_zweimal_automatisiert(): 
    global model
    model = "Oneplus 6 - Android 11 "
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    print(dataframe.groupby("version")["success"].value_counts())
    dataframe['version'] = dataframe['version'].replace([3],'Erste\nAusführung')
    dataframe['version'] = dataframe['version'].replace([4],'Zweite\nAusführung')
    grouped = dataframe.groupby('version')["success"].value_counts().unstack().sort_values([True],ascending=True)
    ax = grouped.plot.barh(stacked=True,color=['slategray', 'powderblue'])
    ax.set_xlabel('Contacted-Domains')
    ax.set_ylabel("")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    ax.plot()
    ax.figure.savefig('automatisiert_zweimal.pdf',bbox_inches='tight')
    plt.show()
   
def apkmitm_patching(apkfile):
    subprocess.run("apk-mitm "+apkfile, shell = True)

def objection_patching(apkfile,method):
    subprocess.run("objection patchapk --source "+apkfile, shell = True)
    startMitmProxy(apkfile,method)
    print("waiting for mitmproxy to set up")
    time.sleep(10) # wait untill mitmproxy is up 
    newapkname = apkfile[:len(apkfile)-4]+".objection.apk"
    packagename = apkfile[:len(apkfile)-4]
    adb_install(newapkname)

 
def frida_patching(apkfile):
    subprocess.run("android-unpinner all "+apkfile,shell=True)
    

def adb_run_objection(apkfile):
    packagename = apkfile[:len(apkfile)-4]
    click.echo(packagename)
    subprocess.run("adb shell monkey -p "+packagename+" -c android.intent.category.LAUNCHER 1  ",shell=True) #auskommentieren für frida alleine
    subprocess.Popen("objection explore --startup-command 'android sslpinning disable'", shell = True)
    subprocess.run("adb push  monkey.sh /data/local/tmp/monkey.sh",shell = True)
    subprocess.run("adb shell chmod +x /data/local/tmp/monkey.sh",shell = True)
    global start
    start = time.time()
    subprocess.run("adb shell /data/local/tmp/monkey.sh", shell = True)



@click.command()
@click.argument('name')
@click.option('--method',nargs=2,help='which method -  choose between : none,apmitm,objection,frida,rooted?')
@click.option('--fromfile',help='which file?')


def main(name,method,fromfile):

    if name == "evaluate":
        click.echo("Reading JSON FILE ...")
        parseJsonFile_emulator_vs_hardware()
    if name == 'download':
            click.echo("reading package names...")
            parseTextFile(fromfile) 

    elif name == 'run':
        startMitmProxy(method[1],method[0])
        if method[0] == "apkmitm":
            click.echo("You choose apkmitm patching with "+method[1])
            apkmitm_patching(method[1])
            newapkname = method[1][:len(method[1])-4]+"-patched.apk"
            adb_install(newapkname) # only install with new apk names
            adb_run((method[1]))
            adb_uninstall_after_time(method[1])
            endMitmProxy()
        
        elif method[0] == "objection":
            click.echo("You choose objection patching with"+method[1])
            objection_patching(method[1],method[0])
            adb_run_objection((method[1]))
            adb_uninstall_after_time(method[1])
            endMitmProxy()

        elif method[0] == "frida":
            click.echo("You choose frida patching with "+method[1])
            frida_patching(method[1])
            endMitmProxy()

        elif  method[0] == "none":
            click.echo("You choose without patching with " +method[1])
            adb_install(method[1])
            adb_run(method[1])
            adb_uninstall_after_time(method[1])
            endMitmProxy()
        
        elif  method[0] == "rooted":
            click.echo("You choose without patching on a rooted device " +method[1])
            adb_install(method[1])
            adb_run(method[1])
            adb_uninstall_after_time(method[1])
            endMitmProxy()








#entry point
if __name__ == "__main__":
    main()





