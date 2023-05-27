import xml.etree.ElementTree as et
import pickle

class ReIDRes(object):

    def __init__(self, ind,path):
        self.ind=pickle.load(open(ind,'rb'))
        self.path=pickle.load(open(path,'rb'))
        self.g_path = self.path['gp']
        self.q_path = self.path['qp']

    def test(self):
        import IPython
        IPython.embed()

class HtmlTree(object):
    doctype_str = "<!DOCTYPE html>"

    def __init__(self):
        self.html_ele = et.Element("html")
        self.head_ele = et.SubElement(self.html_ele, "head")
        self.set_head()
        self.body_ele = et.SubElement(self.html_ele, "body")
        self.table_ele = et.SubElement(self.body_ele,"table")

        self.tbody_ele = et.SubElement(self.table_ele, "tbody")


    def add_line(self,dataset,imgs,clas):
        tr=et.Element('tr')
        tr.append(et.fromstring("<td>{}</td>".format(dataset)))
        for i,c in zip(imgs,clas):
            tr.append(et.fromstring('<td><img class="{}" src="{}" /></td>'.format(c, i.replace('data','imgs'))))
        self.tbody_ele.append(tr)
        self.tbody_ele.append(et.Element('hline'))

    def set_head(self):
        head_str="""
                <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width" />
                <title>RankVis</title>
                <link rel="stylesheet" href="https://cdn.staticfile.org/twitter-bootstrap/4.3.1/css/bootstrap.min.css" />
            
                <script src="https://cdn.staticfile.org/jquery/3.2.1/jquery.min.js"> ;</script>
            
                <script src="https://cdn.staticfile.org/popper.js/1.15.0/umd/popper.min.js"> ;</script>
            
                <script src="https://cdn.staticfile.org/twitter-bootstrap/4.3.1/js/bootstrap.min.js"> ;</script>
            
                <style type="text/css">
                    img {
                            height:128px;
                            border: 3px solid;
                        }
                    img.query {
                            border-color:yellow;
                            }
            
                    img.true {
                            border-color:green;
                            }
            
                    img.false {
                            border-color:red;
                            }
                </style>
            
            </head>
        """

        head_subtree = et.fromstring(head_str)

        # 复制body元素的内容，参考 Element.copy() 函数源码
        self.head_ele.text = head_subtree.text
        self.head_ele.tail = head_subtree.tail
        self.head_ele[:] = head_subtree    # 复制子节点

    def __str__(self):
        html_str = et.tostring(self.html_ele, encoding="unicode")
        return self.doctype_str + '\n' + html_str

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.__str__())


if __name__=='__main__':

    msmt_12 =  ReIDRes('src/path_dict_unrealv12_msmt.pkl','src/paths_msmt_msmt.pkl')
    msmt_123 = ReIDRes('src/path_dict_unrealv123_msmt.pkl', 'src/paths_msmt_msmt.pkl')

    t=HtmlTree()

    def get_line_msmt(data,idx):
        query = data.q_path[idx]
        qid = query.split('/')[-2]
        q_cam = query.split('/')[-1].split('_')[2]
        imgs_ind = data.ind[idx]
        g_imgs=[data.g_path[i] for i in imgs_ind]
        gids = [path.split('/')[-2] for path in g_imgs]
        gcams = [path.split('/')[-1].split('_')[2] for path in g_imgs]
        imgs = [query]
        clas = ['query']

        for i in range(len(g_imgs)):
            if qid==gids[i] and q_cam==gcams[i]:
                continue
            else:
                imgs.append(g_imgs[i])
                clas.append('true' if qid==gids[i] else 'false')


        return imgs, clas


    def get_line(data, idx):
        query = data.q_path[idx]
        qid = query.split('/')[-1].split('_')[0]
        q_cam = query.split('/')[-1].split('_')[1]
        imgs_ind = data.ind[idx]
        g_imgs = [data.g_path[i] for i in imgs_ind]
        gids = [path.split('/')[-1].split('_')[0] for path in g_imgs]
        gcams = [path.split('/')[-1].split('_')[1] for path in g_imgs]
        imgs = [query]
        clas = ['query']

        for i in range(len(g_imgs)):
            if qid == gids[i] and q_cam == gcams[i]:
                continue
            else:
                imgs.append(g_imgs[i])
                clas.append('true' if qid == gids[i] else 'false')

        #
        # imgs = [query]+g_imgs
        # gids = [path.split('/')[-2] for path in g_imgs]
        # clas=['query']+['true' if qid==gid else 'false' for gid in gids]
        return imgs,clas

    for q_idx in msmt_12.ind.keys():

        imgs1, clas1=get_line_msmt(msmt_12,q_idx)


        imgs2, clas2 = get_line_msmt(msmt_123, q_idx)

        t.add_line('U_12', imgs1, clas1)
        t.add_line('U_123', imgs2, clas2)



    t.save('t_compare_3.html')