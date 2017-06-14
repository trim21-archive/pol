/*需要XMLHttpRequest
url:http://bkjws.sdu.edu.cn/b/ksap/xs/vksapxs/pageList
POST
cookies: need
body: aoData[]
Origin: http://bkjws.sdu.edu.cn
Referer: http://bkjws.sdu.edu.cn/f/common/main
*/
let aoData = [
    {
        "name": "sEcho",//似乎用来确定通讯次数的
        "value": 2
    },
    {
        "name": "iColumns",//列数
        "value": 10
    },
    {
        "name": "sColumns",
        "value": ""
    },
    {
        "name": "iDisplayStart",
        "value": 0
    },
    {
        "name": "iDisplayLength",
        "value": 30
    },
    {
        "name": "mDataProp_0",//0列名称
        "value": "ksmc"
    },
    {
        "name": "mDataProp_1",//0列名称
        "value": "kcm"
    },
    {
        "name": "mDataProp_2",//0列名称
        "value": "kch"
    },
    {
        "name": "mDataProp_3",//0列名称
        "value": "kxh"
    },
    {
        "name": "mDataProp_4",//0列名称
        "value": "xqmc"
    },
    {
        "name": "mDataProp_5",//0列名称
        "value": "jxljs"
    },
    {
        "name": "mDataProp_6",//0列名称
        "value": "sjsj"
    },
    {
        "name": "mDataProp_7",//0列名称
        "value": "ksfsmc"
    },
    {
        "name": "mDataProp_8",//0列名称
        "value": "ksffmc"
    },
    {
        "name": "mDataProp_9",//0列名称
        "value": "ksbz"
    },
    {
        "name": "iSortCol_0",//排序的列
        "value": 0
    },
    {
        "name": "sSortDir_0",//排序方式 
        "value": "asc"//asc升序 desc降序
    },
    {
        "name": "iSortCol_1",//似乎是次排序方法...
        "value": 2
    },
    {
        "name": "sSortDir_1",
        "value": "asc"
    },
    {
        "name": "iSortCol_2",//似乎是次次排序
        "value": 3
    },
    {
        "name": "sSortDir_2",
        "value": "asc"
    },
    {
        "name": "iSortingCols",
        "value": 3
    },
    {
        "name": "bSortable_0",//考试名称
        "value": true
    },
    {
        "name": "bSortable_1",//课程名
        "value": false
    },
    {
        "name": "bSortable_2",//课程号
        "value": true
    },
    {
        "name": "bSortable_3",//课序号
        "value": true
    },
    {
        "name": "bSortable_4",//所属校区
        "value": false
    },
    {
        "name": "bSortable_5",//考试地点
        "value": false
    },
    {
        "name": "bSortable_6",//考试时间
        "value": true
    },
    {
        "name": "bSortable_7",//考试方法(开闭卷)
        "value": false
    },
    {
        "name": "bSortable_8",//考试方法(成绩占比)
        "value": false
    },
    {
        "name": "bSortable_9",//考试备注
        "value": false
    },
    {
        "name": "xnxq",//学期学年
        "value": "2016-2017-2"
    },
    {
        "name": "ksrwid",//考试任务
        "value": "000000005bf6cb6f015bfac609410d4b" //期末考试
    }
]