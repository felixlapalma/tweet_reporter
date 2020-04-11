#!/usr/bin/env python
# coding: utf-8

# # tweet_informer_provincia_ciudad

# In[ ]:


from tweet_informer_lib import os, wget,shutil,pd,glob,sys,zipCompressDir,datetime
from tweet_informer_lib import make_cammesa_url,make_plt_provincia_capital
from tweet_informer_lib import json,tweepy


# In[ ]:


#
opt=sys.argv[1:2][0]
print(opt)

# In[ ]:


# get Opt
#opt='Chaco'


# In[ ]:


pd_cfg=pd.read_csv('cfg/csv_cfg_provincias.csv',index_col=0)
prov_dict=pd_cfg.T.to_dict()


# ### url

# In[ ]:


url_dict={}
if opt in prov_dict:
    provincia,capital=prov_dict[opt]['Total'],prov_dict[opt]['Capital']
    make_cammesa_url('provincia',provincia,url_dict)
    make_cammesa_url('capital',capital,url_dict)
else:
    'Opciones validas: {}'.format(list(prov_dict.keys()))
    sys.exit()


# ### make dirs

# In[ ]:


tmp='tmp'+opt
arxive='arxive'
for folder in [arxive,tmp]:
    os.makedirs(folder,exist_ok=True)


# ### get data

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
    shutil.rmtree(tmp)
    sys.exit('No CSV files')


# ### data proc

# In[ ]:


pd_ciudad=pd.read_csv(csv_dict['capital'],sep=';',decimal=',',index_col=[0],parse_dates=[0])
pd_provincia=pd.read_csv(csv_dict['provincia'],sep=';',decimal=',',index_col=[0],parse_dates=[0])


# In[ ]:


pd_merge=pd.merge(pd_provincia,pd_ciudad,left_index=True,right_index=True,suffixes=('_prov','_capital'))
pd_merge[pd_merge < 0] = 0
pd_merge['provincia_sin_capital']=pd_merge['Dem Hoy_prov']-pd_merge['Dem Hoy_capital']
pd_merge_not_na=pd_merge.dropna()


# In[ ]:


if len(pd_merge_not_na)>10:
    pass
else:
    shutil.rmtree(tmp)
    sys.exit('Short Dataframe')


# In[ ]:

try:
    fig,tweet_text=make_plt_provincia_capital(pd_merge_not_na,opt,figsize=(16,12))
    # save fig
    figName=os.path.join(tmp,'consumo.png')
    fig.savefig(figName,transparent=False)
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
        tweet =tweet_text
        image_path =figName
        # to attach the media file 
        status = twitter.update_with_media(image_path, tweet)
except:
    shutil.rmtree(tmp)
    sys.exit('Failed to TWEET')


# ### Compress - Save - Delete

# In[ ]:


zipname=os.path.join(arxive,req_time+'_consumo_'+opt+'.zip')
zipCompressDir(zipname,tmp)


# In[ ]:


shutil.rmtree(tmp)

