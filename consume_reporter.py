#!/usr/bin/env python
# coding: utf-8

# # tweet_informer

# In[ ]:


from tweet_informer_lib import os, wget,shutil,pd,make_plt_cba,glob,sys,zipCompressDir,datetime
from tweet_informer_lib import json,tweepy


# ### make dirs

# In[ ]:


tmp='tmp'
arxive='arxive'
for folder in [arxive,tmp]:
    os.makedirs(folder,exist_ok=True)


# ### url

# In[ ]:


url_dict={}
url_dict.update({'provincia_cba':'https://aplic.cammesa.com/complemento-portal/descargar?type=csv&value=ChtDem_0145.xml&header=datosDemandas',
                 'ciudad_cba':'https://aplic.cammesa.com/complemento-portal/descargar?type=csv&value=ChtDem_0149.xml&header=datosDemandas'})


# In[ ]:


csv_dict={}
req_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
for key in url_dict:
    filename=os.path.join(tmp,key+'.csv')
    filesaved = wget.download(url_dict[key],out=filename)
    csv_dict.update({key:filesaved})


# In[ ]:


csv_=glob.glob(os.path.join(tmp,'*.csv'))
if len(csv_)==2:
    pass
else:
    sys.exit('No CSV files')


# ### Data Proc

# In[ ]:


pd_ciudad=pd.read_csv(csv_dict['ciudad_cba'],sep=';',decimal=',',index_col=[0],parse_dates=[0])
pd_provincia=pd.read_csv(csv_dict['provincia_cba'],sep=';',decimal=',',index_col=[0],parse_dates=[0])


# In[ ]:


pd_merge=pd.merge(pd_provincia,pd_ciudad,left_index=True,right_index=True,suffixes=('_prov','_ciudad'))
pd_merge['provincia_sin_ciudad']=pd_merge['Dem Hoy_prov']-pd_merge['Dem Hoy_ciudad']
pd_merge_not_na=pd_merge.dropna()


# In[ ]:


fig,tweet_text=make_plt_cba(pd_merge_not_na,figsize=(16,12))


# In[ ]:


# save fig
figName=os.path.join(tmp,'consumo.png')
fig.savefig(figName,transparent=False)


# ### Tweeter Stuff

# In[ ]:


config_file = '.tweepy.json'
with open(config_file) as fh:
    config = json.load(fh)


# In[ ]:


auth = tweepy.OAuthHandler(
    config['consumer_key'], config['consumer_secret']
)
auth.set_access_token(
    config['access_token'], config['access_token_secret']
)

twitter = tweepy.API(auth)


# In[ ]:


tweet =tweet_text
image_path =figName


# In[ ]:


# to attach the media file 
status = twitter.update_with_media(image_path, tweet)  
twitter.update_status(status = tweet)


# ### Compress - Save - Delete

# In[ ]:


zipname=os.path.join(arxive,req_time+'_consumo_cba.zip')
zipCompressDir(zipname,tmp)


# In[ ]:


shutil.rmtree(tmp)

