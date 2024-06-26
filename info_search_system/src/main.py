import os  
import sys  
import jieba  
from collections import defaultdict 
import string 
import math
from termcolor import colored
import json
from tyc import chinese_punctuations 
# 定义中文标点符号集合
# chinese_punctuations = "，。！？、；：“”‘’（）《》〈〉【】『』「」的 把 被 为 啊 呢"

all_punctuations = string.punctuation + chinese_punctuations

class InvertedIndexBuilder:
    def __init__(self, directory):
        self.directory = directory  # 文档所在目录
        self.inverted_index = defaultdict(lambda: defaultdict(list))  # 倒排索引，包含单词位置信息
        self.document_frequencies = defaultdict(int)  # 每个词的文档频率
        self.num_documents = 0  # 文档总数
        self.term_frequencies = defaultdict(int) # 每篇文档中的单词个数
        self.metadata = {} #文档元数据

    def build(self):
        # 读取目录中的所有文件
        files = os.listdir(self.directory)
        txt_files = [f for f in files if f.endswith('.txt')]

        # 遍历每个文件
        for txt_file in txt_files:
            file_id = os.path.splitext(txt_file)[0]  # 移除文件扩展名获取文件ID
            file_path = os.path.join(self.directory, txt_file)  # 获取文件路径

            # 打开并读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                title = lines[0].strip().split(":")[1]
                self.metadata[file_id] = {
                    "title": title
                    }
                # content = file.read()
                content = ''.join(lines[1:]).strip("简介")  #简介：后面
            words = jieba.lcut(content)  # 使用jieba分词
            words = [word for word in words if word not in all_punctuations and not word.isspace()]  # 去除标点和空白
            unique_words = set(words)  # 获取文件中的唯一词

            # 更新每个词的文档频率
            for word in unique_words:
                self.document_frequencies[word] += 1

            
            # 更新倒排索引和位置信息
            for position,word in enumerate(words):
                self.inverted_index[word][file_id].append(position)
         
            self.term_frequencies[file_id]=len(words)
            self.num_documents += 1  # 更新文档总数

    def compute_tf_idf(self, query_terms):

        tf_idf_scores = defaultdict(float)  # 初始化查询TF-IDF得分字典

        # 遍历查询中的每个词
        for term in query_terms:
            # 如果词在倒排索引中
            for doc_id, position_list in self.inverted_index.get(term, {}).items():
                # 计算词频(TF)
                tf = len(position_list)/ self.term_frequencies[doc_id]
                # 计算逆文档频率(IDF)
                idf = math.log(self.num_documents / (1 + self.document_frequencies.get(term, 0)))
                # 计算TF-IDF并累加到文档得分中
                tf_idf_scores[doc_id] += tf * idf

        return tf_idf_scores # 返回查询的TF-IDF得分

      
    def search(self, query_terms):
        tf_idf_scores = self.compute_tf_idf(query_terms)  # 计算查询的TF-IDF得分
        # 按得分排序并返回
        sorted_scores = sorted(tf_idf_scores.items(), key=lambda x: x[1], reverse=True)

        results_with_context = []
        for doc_id, score in sorted_scores:
            i=0
            context = []
            while i<len(query_terms): 
                if query_terms[i] in self.inverted_index.keys():
                    context.extend(self.get_context(doc_id, query_terms,i))
                i+=1
            results_with_context.append((doc_id, score, context))

        return results_with_context
    

#获取上下文
    def get_context(self, doc_id, query_terms,i, window_size=5):
        term=query_terms[i]
        file_path = os.path.join(self.directory, f"{doc_id}.txt")
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            content=''.join(lines[1:]).strip("简介")

        words = jieba.lcut(content)
        words = [word for word in words if word not in all_punctuations and not word.isspace()]  # 去除标点和空白
 
        positions = self.inverted_index[term][doc_id]
        context_snippets = []
        for position in positions:
            start = max(0, position - window_size)
            end = min(len(words), position + window_size + 1)
            snippet = words[start:end]
            # 将查询词染红
            snippet = [colored(word, 'red') if word in query_terms else word for word in snippet]
            context_snippets.append("".join(snippet))
        return context_snippets

    def print_inverted_index(self):
        # 打印倒排索引
        for word, posting_list in self.inverted_index.items():
            print(f"{word}: ", end="")
            for doc_id, positions in posting_list.items():
                print(f"{doc_id}: {positions}", end=",")
            print()


def evaluate(query_terms):
    rating = input("请评价检索结果准确率 (1-5): ")
    feedback={"query":query_terms,"rating":rating}
    return feedback




if __name__ == "__main__":
    # 检查是否有命令行参数指定数据路径
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    else:
        data_path = 'src/files/News'

    # 输出当前工作目录
    current_working_directory = os.getcwd()
    print(f"Current working directory: {current_working_directory}")

    directory = data_path  # 设置文档目录
    builder = InvertedIndexBuilder(directory)  # 创建倒排索引构建器
    builder.build()  # 构建倒排索引
    builder.print_inverted_index()  # 打印倒排索引
    while True:
        opt=input("选择操作:   [0]:退出     [1]:直接查询        [2]:分词查询\n")
        if(opt=='0'):
            break
        elif(opt=='2'):
            query = input("输入你的 query:")  # 获取用户查询
            query_terms = jieba.lcut(query)  # 对查询进行分词
            query_terms = [term for term in query_terms if term not in all_punctuations and not term.isspace()]  # 去除标点和空白
            print(query_terms)
            for term in query_terms:
                print(term,":")
                results = builder.search([term])  # 搜索查询
                for doc_id, score, context in results:
                    print(f"Document: {doc_id}, TF_IDF相关度: {score}")
                    print(f"Title: {builder.metadata[doc_id]['title']}")
                    print("上下文:")
                    for ctx in context:
                        print(f"{ctx}...",end="")
                    print()
        elif(opt=='1'):
            query = input("输入你的 query:")  # 获取用户查询
            query_terms = jieba.lcut(query)  # 对查询进行分词
            query_terms = [term for term in query_terms if term not in all_punctuations and not term.isspace()]  # 去除标点和空白
            print(query_terms)
            results = builder.search(query_terms)  # 搜索查询
            for doc_id, score,context in results:
                print(f"Document: {doc_id}, TF_IDF相关度: {score}")
                print(f"Title: {builder.metadata[doc_id]['title']}")
                print("上下文:")
                for ctx in context:
                        print(f"{ctx}...",end="")
                print()
            choose=input(colored("准确率评价？  [Y/N]:","blue"))
            if choose=="Y" or choose=="y":
                feedback=evaluate(query_terms)
                with open('feedback.json', 'a', encoding='utf-8') as f:
                    json.dump(feedback, f, ensure_ascii=False, indent=4)


           
