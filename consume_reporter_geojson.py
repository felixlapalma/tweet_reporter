#!/usr/bin/env python
# coding: utf-8

# # tweet_informer_provincia_ciudad

# In[ ]:


from tweet_informer_lib import os, wget,shutil,pd,glob,sys,zipCompressDir,datetime
from tweet_informer_lib import make_cammesa_url,make_plt_provincia_capital_bars,cammesa_consume_reader
from tweet_informer_lib import json,tweepy,reduce,plt,gpd,unidecode,gplt,make_cammesa_url_v2


# In[ ]:


pd_cfg=pd.read_csv('cfg/csv_cfg_provincias.csv',index_col=0)
prov_dict=pd_cfg.T.to_dict()


# In[ ]:


df_prov=gpd.read_file('cfg/provincia.geojson')
df_prov.NAM=df_prov.NAM.apply(unidecode.unidecode)


# ### url

# In[ ]:


url_dict={}
for opt in prov_dict:
    url_dict.update({opt:{}})
    provincia,url_case=prov_dict[opt]['Total'],prov_dict[opt]['url']
    make_cammesa_url_v2('provincia',provincia,url_dict[opt],url_case)


# ### make dirs

# In[ ]:


tmp='tmp_mapa'
arxive='arxive'
for folder in [arxive,tmp]:
    os.makedirs(folder,exist_ok=True)


# ### get data

# In[ ]:


csv_dict={}
req_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
for p in url_dict:
    csv_dict.update({p:{}})
    for key in url_dict[p]:
        filename=os.path.join(tmp,p+'_'+key+'.csv')
        filesaved = wget.download(url_dict[p][key],out=filename)
        csv_dict[p].update({key:filesaved})


# In[ ]:


csv_=glob.glob(os.path.join(tmp,'*.csv'))
if len(csv_)>0:
    pass
else:
    shutil.rmtree(tmp)
    sys.exit('No CSV files')


# ### data proc

# In[ ]:


aux=[]
for p in csv_dict:
    if p in ['Buenos Aires','SADI','GBA']:
        drop=[1,2,3,4]
    else:
        drop=[1,2]
    df=cammesa_consume_reader(csv_dict[p]['provincia'],drop)
    df.columns=[p]
    aux.append(df)
df=reduce(lambda x, y: pd.merge(x, y, left_index=True,right_index=True), aux)
df[df < 0] = 0
df_notna=df.dropna()


# In[ ]:


df_notna=df_notna.dropna()


# In[ ]:


series=df_notna.iloc[-1]
series_time=series.name.strftime('%d-%m-%Y %H:%M:%S')
df_new=pd.DataFrame(df_notna.iloc[-1]).reset_index()
df_new.columns=['NAM','Consumo']
df_new['Consumo_Porc']=df_new['Consumo']/df_notna['SADI'].iloc[-1]*100
df_new['NAM']=df_new['NAM'].apply(lambda x: x if x!='GBA' else 'Ciudad Autonoma de Buenos Aires')


# In[ ]:


df_filt=df_prov.merge(df_new,on='NAM')
if len(df_filt)>1:
    pass
else:
    shutil.rmtree(tmp)
    sys.exit('Short Dataframe')

# In[ ]:


try:
    fig=plt.figure(figsize=(15, 18))
    ax=fig.add_subplot(111)
    ax_gpd=gplt.choropleth(df_filt, hue=df_filt['Consumo_Porc'],cmap='Oranges',k=None,ax=ax)
    for p in df_filt.NAM:
        x=df_filt[df_filt.NAM==p].geometry.representative_point().x
        y=df_filt[df_filt.NAM==p].geometry.representative_point().y
        MW_porc=df_filt[df_filt.NAM==p]['Consumo_Porc'].values
        MW=df_filt[df_filt.NAM==p]['Consumo'].values
        if MW_porc[0]>1/22*100:
            c='red'
        else:
            c='black'    
        if p=='Ciudad Autonoma de Buenos Aires':
            fmt='GBA: {:.0f}\n({:.1f}%)'
        else:
            fmt='{:.0f}\n({:.1f}%)'
        ax_gpd.text(x,y,fmt.format(MW[0],MW_porc[0]),horizontalalignment='center',verticalalignment='bottom',bbox=dict(facecolor='white', alpha=0.7),fontsize=14,color=c)
        ax_gpd.set_title('Demanda Provincias [MW] \n(% Total Pais) \n'+series_time,fontsize=20)
    # save fig
    figName=os.path.join(tmp,'mapa_consumo.png')
    fig.savefig(figName,transparent=True)
except:
    shutil.rmtree(tmp)
    print('Plot ERROR')
    sys.exit('Plot ERROR')   


# ### tweeter Stuff

# In[ ]:


#
config_file = 'cfg/.tweepy.json'
try:
    with open(config_file) as fh:
        config = json.load(fh)
        auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
        auth.set_access_token(config['access_token'], config['access_token_secret'])
        twitter = tweepy.API(auth)
        tweet ='Demanda Provincias [MW] y % Total Pais'
        image_path =figName
        # to attach the media file 
        status = twitter.update_with_media(image_path, tweet)
except:
    shutil.rmtree(tmp)
    sys.exit('Failed to TWEET')


# ### Compress - Save - Delete

# In[ ]:


zipname=os.path.join(arxive,req_time+'_consumo_mapa_provincias.zip')
zipCompressDir(zipname,tmp)


# In[ ]:


shutil.rmtree(tmp)

