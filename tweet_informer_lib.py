import wget
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import shutil
import matplotlib.gridspec as gridspec
import glob
import sys
import zipfile as ziphlr
import tweepy,json
import geopandas as gpd
import unidecode as unidecode
import geoplot as gplt
#
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from functools import reduce

def make_cammesa_url(case,caseNum,dict_to_update):
    """
    """
    caseNum=int(caseNum)
    base='https://aplic.cammesa.com/complemento-portal/descargar?type=csv&value=ChtDem_'
    num='{0:04d}'.format(caseNum)
    end='.xml&header=datosDemandas'
    url=base+num+end
    dict_to_update.update({case:url})

def make_cammesa_url_v2(case,caseNum,dict_to_update,url_case=0):
    """
    """
    caseNum=int(caseNum)
    if url_case==0:
        base='https://aplic.cammesa.com/complemento-portal/descargar?type=csv&value=ChtDem_'
        end='.xml&header=datosDemandas'
    elif url_case==1:
        base='https://aplic.cammesa.com/complemento-portal/descargar?type=csv&value=ChtDemandaArea5Min_'
        end='.xml&header=datosDemandasPreDes'
    num='{0:04d}'.format(caseNum)
    url=base+num+end
    dict_to_update.update({case:url})
   
    
def zipCompressDir(zipFullName,dirPath):
     # Open Zip file for append
    zipt = ziphlr.ZipFile(zipFullName,'a',ziphlr.ZIP_DEFLATED)
    # append
    (path, _, filenames) = next(os.walk(dirPath)) 
    
    for xfile in filenames:
        fpath=os.path.join(path,xfile)
        zipt.write(fpath, os.path.basename(fpath))
    # Zip Close
    zipt.close()

def format_axes(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        ax.tick_params(labelbottom=False, labelleft=False)

def make_plt_cba(pd_in,figsize=(10,8),font_line_graph=18,font_pie=14):
    """
    """
    fontprim=font_line_graph
    font_pie=font_pie
    # gridspec inside gridspec
    f = plt.figure(figsize=figsize)
    
    gs0 = gridspec.GridSpec(1, 1, figure=f)
    gs00 = gridspec.GridSpecFromSubplotSpec(3, 3, subplot_spec=gs0[0])
    ax1 = f.add_subplot(gs00[:-1, :])
    ax2 = f.add_subplot(gs00[-1, 0])
    ax3 = f.add_subplot(gs00[-1, 1])
    ax4 = f.add_subplot(gs00[-1, -1])
    #
    pds=len(pd_in)
    cases=[0,int(pds/2),pds-1]
    #
    pd_in[['Dem Hoy_prov','provincia_sin_ciudad','Dem Hoy_ciudad']].plot(ax=ax1,style='-.',lw=4)
    #pd_in['provincia_sin_ciudad'].plot(ax=ax1,style='-.',lw=3)
    #pd_in['Dem Hoy_ciudad'].plot(ax=ax1,style='-.',lw=3)
    ax1.grid(True)
    ax1.tick_params(axis='both',which='both',labelsize=fontprim,)
    ax1.set_xlabel('Tiempo',fontsize=fontprim)
    ax1.set_ylabel('Demanda Real [MW]',fontsize=fontprim)
    ax1.legend(['Provincia','Prov. SIN Capital','Capital'],fontsize=14,title='Demanda',title_fontsize=12,fancybox=True, framealpha=0.)
    # title
    dini=pd_in.index[0].strftime('%d-%m-%Y %H:%M');dend=pd_in.index[-1].strftime('%d-%m-%Y %H:%M')
    title='Demanda Real [MW] - Provincia de Córdoba \n'+dini +'-' + dend
    ax1.set_title(title,fontsize=fontprim)
    # Pie
    explode = (0, 0.1)
    for i,axi in zip(cases,[ax2,ax3,ax4]):
        #
        pdi=pd_in[['provincia_sin_ciudad','Dem Hoy_ciudad']].iloc[i,:]
        pdi.plot(kind='pie',
                                                                        explode=explode,
                                                                        ax=axi,
                                                                        labels=['Prov. SIN Capital','Capital'],
                                                                        fontsize=font_pie,
                                                                        autopct=lambda p : '{:.1f}%\n({:,.0f})'.format(p,p * sum(pdi)/100),
                                                                        colors=['orange','green'],
                                                                        startangle=90,shadow=False)
        
        axi.set_xlabel(axi.get_ylabel(),fontsize=font_pie)
        axi.set_ylabel('')
    plt.tight_layout()
    # Assemble Msg
    time_text=pd_in[['Dem Hoy_prov','provincia_sin_ciudad','Dem Hoy_ciudad']].iloc[-1].name.strftime('%d-%m-%Y %H:%M')
    values=pd_in[['Dem Hoy_prov','provincia_sin_ciudad','Dem Hoy_ciudad']].iloc[-1].values
    text=['Demanda (MW) - ',time_text,' - ']
    for i,v in zip(['Total Provincia Cba','Provincia sin Capital','Capital'],values):
        t='{}: {:.1f} /'.format(i,v)
        text.append(t)
    tweet_text=' '.join(text)
    return f,tweet_text


def make_plt_provincia_capital(pd_in,provincia,figsize=(10,8),font_line_graph=18,font_pie=14):
    """
    """
    fontprim=font_line_graph
    font_pie=font_pie
    # gridspec inside gridspec
    f = plt.figure(figsize=figsize)
    
    gs0 = gridspec.GridSpec(1, 1, figure=f)
    gs00 = gridspec.GridSpecFromSubplotSpec(3, 3, subplot_spec=gs0[0])
    ax1 = f.add_subplot(gs00[:-1, :])
    ax2 = f.add_subplot(gs00[-1, 0])
    ax3 = f.add_subplot(gs00[-1, 1])
    ax4 = f.add_subplot(gs00[-1, -1])
    #
    pds=len(pd_in)
    cases=[0,int(pds/2),pds-1]
    #
    pd_in[['Dem Hoy_prov','provincia_sin_capital','Dem Hoy_capital']].plot(ax=ax1,style='-.',lw=4)
    #pd_in['provincia_sin_ciudad'].plot(ax=ax1,style='-.',lw=3)
    #pd_in['Dem Hoy_ciudad'].plot(ax=ax1,style='-.',lw=3)
    ax1.grid(True)
    ax1.tick_params(axis='both',which='both',labelsize=fontprim,)
    ax1.set_xlabel('Tiempo',fontsize=fontprim)
    ax1.set_ylabel('Demanda Real [MW]',fontsize=fontprim)
    ax1.legend(['Provincia','Prov. SIN Capital','Capital'],fontsize=14,title='Demanda',title_fontsize=12,fancybox=True, framealpha=0.)
    # title
    dini=pd_in.index[0].strftime('%d-%m-%Y %H:%M');dend=pd_in.index[-1].strftime('%d-%m-%Y %H:%M')
    title='Demanda Real [MW] - Provincia de '+ provincia + ' \n'+dini +'-' + dend
    ax1.set_title(title,fontsize=fontprim)
    # Pie
    explode = (0, 0.1)
    for i,axi in zip(cases,[ax2,ax3,ax4]):
        #
        pdi=pd_in[['provincia_sin_capital','Dem Hoy_capital']].iloc[i,:]
        pdi.plot(kind='pie',
                                                                        explode=explode,
                                                                        ax=axi,
                                                                        labels=['Prov. SIN Capital','Capital'],
                                                                        fontsize=font_pie,
                                                                        autopct=lambda p : '{:.1f}%\n({:,.1f})'.format(p,p * sum(pdi)/100),
                                                                        colors=['orange','green'],
                                                                        startangle=0,shadow=False)
        
        axi.set_xlabel(axi.get_ylabel(),fontsize=font_pie)
        axi.set_ylabel('')
    plt.tight_layout()
    # Assemble Msg
    cols=['Dem Hoy_prov','provincia_sin_capital','Dem Hoy_capital']
    time_text=pd_in[cols].iloc[-1].name.strftime('%d-%m-%Y %H:%M')
    values=pd_in[cols].iloc[-1].values
    text=[provincia,' - Demanda (MW) - ',time_text,' - ']
    for i,v in zip(['Total Provincia','Provincia sin Capital','Capital'],values):
        t='{}: {:.1f} /'.format(i,v)
        text.append(t)
    tweet_text=' '.join(text)
    return f,tweet_text
 
 
def make_plt_provincia_capital_bars(pd_in,title,figsize=(10,8),font_line_graph=16,font_pie=14):
    """
    """
    fontprim=font_line_graph
    font_pie=font_pie
    # gridspec inside gridspec
    fig = plt.figure(figsize=figsize)
    ax= fig.add_subplot(111)
    pd_in[['Capital','Provincia_SIN_Capital']].plot(ax=ax,kind='bar',color=['g','orange'])
    # title
    ax.set_title(title,fontsize=fontprim)
    ax.grid(True)
    ax.tick_params(axis='both',which='both',labelsize=fontprim)
    ax.set_ylabel('Demanda Real [MW]',fontsize=fontprim)
    plt.tight_layout()
    return fig
    
def cammesa_consume_reader(name,drop_cols=[]):
    df=pd.read_csv(name,sep=';',decimal=',',index_col=[0],parse_dates=[0])
    df.drop(df.columns[drop_cols],axis=1,inplace=True)
    return df
