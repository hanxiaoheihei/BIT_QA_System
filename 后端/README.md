# BIT OPEN-DOMAIN QA

## Introduction
* Here is our group's project for CCF & Baidu 2019 Reading Comprehension Competition. We apply the competition models to build a open domain QA system, which can process the query-related docs from search engine and output short and informative answers. You can ask any questions you want here. 
* This project provide you the training scripts for LIC 2019, a demo server and the pretrained models. Weather you want to study the reading comprehension problem in DuReader dataset or build a open domain QA engine, you can find what you want here.
* [Paper](http://tcci.ccf.org.cn/conference/2019/papers/EV12.pdf) was accepted by NLPCC2019.

## Get Started
1. Download [model files](https://drive.google.com/open?id=1EsRZjUDlXRifYOjZhfjdhQYPHyuPE5dN):`chinese_L-12_H-768_A-12`, `mrc_model` and `rerank_model`. Then unzip and move to`checkpoints`directory. Finally the project structure will be:
```bash
.
├── checkpoints
│   ├── chinese_L-12_H-768_A-12
│   │   ├── config.json
│   │   ├── pytorch_model.bin
│   │   └── vocab.txt
│   ├── mrc_model
│   │   ├── config.json
│   │   ├── pytorch_model.bin
│   │   └── vocab.txt
│   └── rerank_model
│       ├── config.json
│       ├── pytorch_model.bin
│       └── vocab.txt
...
```
2. Change config file: `config.py`
3. Run the server: `python server.py --config_path=config_v2.json --port=7892`
4. Run the server on gpu: `CUDA_VISIBLE_DEVICES=0 nohup python server.py --config_path=config_v2.json --port=7892`
5. Example for open domain QA (GET & POST): `101.124.42.34:7892/api/func1?query=西红柿炒蛋的做法？`
6. Example for doc based QA (only POST): 
    * `101.124.42.34:7892/api/func2`
    * ```{"querys": ["北理工成立时间？","北理工有多少学生？","北理工博后站点有多少？"], "doc": "北京理工大学（Beijing Institute of Technology）是中国共产党创办的第一所理工科大学，隶属于中华人民共和国工业和信息化部，是全国重点大学，首批进入国家“211工程”、“985工程”，首批进入世界一流大学建设高校A类行列，入选学位授权自主审核单位、高等学校学科创新引智计划、高等学校创新能力提升计划、卓越工程师教育培养计划、国家建设高水平大学公派研究生项目、国家大学生创新性实验计划、国家级大学生创新创业训练计划、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校、首批高等学校科技成果转化和技术转移基地，工业和信息化部高校联盟、中国人工智能教育联席会成员。北京理工大学前身是1940年成立于延安的自然科学院，历经晋察冀边区工业专门学校、华北大学工学院等办学时期，1949年定址北京并接收中法大学校本部和数理化三个系，1952年定名为北京工业学院，1988年更名为北京理工大学。截至2019年6月，学校占地188公顷，建筑面积161万平方米，图书馆馆藏274.9万册，固定资产总额64.47亿元；教职工总数3376人，其中专任教师2275人；有全日制在校生27678人，其中本科生14717人，硕士生8039人，博士生3884人，学位留学生1038人；设有18个专业学院以及徐特立学院；开办70个本科专业；拥有一级学科博士学位授权点27个，博士专业学位授权点4个，一级学科硕士学位授权点30个，硕士专业学位授权点6个，博士后科研流动站18个。"}```
    * `101.124.42.34:7892/api/func3`
    * ```{"query": "北理工成立时间？", "docs": ["北京理工大学（Beijing Institute of Technology）是中国共产党创办的第一所理工科大学，隶属于中华人民共和国工业和信息化部，是全国重点大学，首批进入国家“211工程”、“985工程”，首批进入世界一流大学建设高校A类行列，入选学位授权自主审核单位、高等学校学科创新引智计划、高等学校创新能力提升计划、卓越工程师教育培养计划、国家建设高水平大学公派研究生项目、国家大学生创新性实验计划、国家级大学生创新创业训练计划、新工科研究与实践项目、中国政府奖学金来华留学生接收院校、全国深化创新创业教育改革示范高校、首批高等学校科技成果转化和技术转移基地，工业和信息化部高校联盟、中国人工智能教育联席会成员。北京理工大学前身是1940年成立于延安的自然科学院，历经晋察冀边区工业专门学校、华北大学工学院等办学时期，1949年定址北京并接收中法大学校本部和数理化三个系，1952年定名为北京工业学院，1988年更名为北京理工大学。截至2019年6月，学校占地188公顷，建筑面积161万平方米，图书馆馆藏274.9万册，固定资产总额64.47亿元；教职工总数3376人，其中专任教师2275人；有全日制在校生27678人，其中本科生14717人，硕士生8039人，博士生3884人，学位留学生1038人；设有18个专业学院以及徐特立学院；开办70个本科专业；拥有一级学科博士学位授权点27个，博士专业学位授权点4个，一级学科硕士学位授权点30个，硕士专业学位授权点6个，博士后科研流动站18个。", "原材料：基体采用高强度挤压铝合金，优质锌合金，超强防腐不锈钢及优质碳素结构钢，部分零件采用性能优良的聚酰胺、聚甲醛等工程塑料。表面处理：表面进行电镀或喷涂等防腐处理，防腐实验轻易超过行业标准的中性盐雾防腐要求72H。结构：独特的结构设计，在满足市场大多数型材需求时，能够实现自动化/半自动化生产。技术服务：我们针对不同区域的需求提供多方面的技术服务。价格：目前根据产品类别不同，价格从低到高有划分不同档次的产品，普通类型的单滑轮3.8元/件，双滑轮7.6元/件。"]}```


## TODO LIST
- [ ] Deploy two bert model by tensorflow serving
