# -*- coding:utf-8 -*-
# selenium, phantomjsを使ってスクレイピングする
# 対象はSciencedirectウェブサイト内にある
# journal_id
# Cognition: 00100277
# 
# フレームワークを使う
import lxml.html as lh
from nltk.tokenize import RegexpTokenizer as rt
import datetime as dt

# アブストラクトを取得するスクリプトセット
# journal_id: sciencedirect内でのジャーナルのid
# journal_name: ジャーナル名（半角英数）
# dbname: データベース名（半角英数）
# max_vol: 10区切りでの最大のボリューム数（133のときは130）
# min_vol: 10区切りでの最小のボリューム数（10）
# Pymongoが必須です．

class Scraper:
    def __init__(self,journal_id,log_filepath,abstract_collection,browser):
        self.journal_id = journal_id
        self.abstract_class = 'svAbstract'
        self.title_class = 'svTitle'
        self.author_class = 'authorName'
        self.log_filepath = log_filepath
        self.abstract_collection = abstract_collection
        self.volissue_class = 'volIssue'
        self.date_variable = 'SDM.pm.coverDate = '
        self.doi_variable = 'SDM.doi = '
        self.browser = browser
    # ボリュームからイシューのリンクを取得する
    def get_issue_links(self,volume_link):
        issue_links = []
        volume_content = self.get_source(volume_link)
        volume_anchors = volume_content.xpath('//a')
        for anchor in volume_anchors:
            if 'href' in anchor.attrib and anchor.text:
                if '/journal/' + self.journal_id in anchor.attrib['href'] and 'http' not in anchor.attrib['href']:
                    issue_links.append('http://www.sciencedirect.com'+anchor.attrib['href'])
        self.logging('Finish to get issue links from ' + volume_link + ' at ' + self.get_now())
        return list(set(issue_links))
    
    # イシューごとにリンクを収集する
    def get_article_links(self,issue_link):
        article_links = []
        issue_content = self.get_source(issue_link)
        issue_anchors = issue_content.xpath('//a')
        for anchor in issue_anchors:
            if 'href' in anchor.attrib and anchor.text:
                if '/pii/' in anchor.attrib['href']:
                  article_links.append(anchor.attrib['href'])
        self.logging('Finish to get article links from ' + issue_link + ' at ' + self.get_now())
        return list(set(article_links))
    
    # アブストをリンクから取得する（Bigramなどへも変換する）
    def get_abstract(self,article_link):
        article_content = self.get_source(article_link)
        raw_abstract = self.parse_abstract(article_content)
        utf_abstract = self.get_utf(raw_abstract)
        raw_words = self.get_token(raw_abstract)
        words = [self.get_utf(word) for word in raw_words]
        raw_title = self.parse_title(article_content)
        title = self.get_utf(raw_title)
        raw_volissue = self.parse_volissue(article_content)
        volissue = self.get_utf(raw_volissue)
        raw_date = self.parse_date(article_content)
        pub_date = self.get_utf(raw_date)
        raw_doi = self.parse_doi(article_content)
        doi = self.get_utf(raw_doi)
        authors_unicode = self.parse_author(article_content)
        authors = [self.get_utf(author) for author in authors_unicode]
        char_bigrams_unicode = self.get_char_bigram(raw_abstract)
        char_bigrams = [self.get_utf(bigram) for bigram in char_bigrams_unicode]
        word_bigrams_unicode = self.get_word_bigram(raw_words)
        word_bigrams = [self.get_utf(bigram) for bigram in word_bigrams_unicode]
        self.abstract_collection.save({'title':title,'authors':authors,'doi':doi,'pub_date':pub_date,'volissue':volissue,'raw':utf_abstract,'chbigm':char_bigrams,'wdbigm':word_bigrams,'words':words})
        self.logging('Finish to get abstract from ' + title + ' ('+ pub_date+', '+ article_link+') at ' + self.get_now())
        return title
    
    # target_urlにアクセスしてソースを返す
    def get_source(self,target_url):
        self.browser.get(target_url)
        content = self.browser.page_source
        root = lh.fromstring(content)
        return root
    
    # テキストをutf-8にエンコードする
    def get_utf(self,unicode_str):
        return unicode_str.encode('utf-8')
    
    # 著者を生のhtmlからパースする
    def parse_author(self,root):
        author_anchors = root.xpath('//a[contains(@class,"'+self.author_class+'")]')
        authors = []
        try:
            for anchor in author_anchors:
                authors.append(anchor.text)
            return authors
        except:
            return []
    
    
    # volume issue 年月を取得
    def parse_volissue(self,root):
        volissue_cont = root.xpath('//p[contains(@class,"'+self.volissue_class+'")]')
        try:
            volissue_str = lh.tostring(volissue_cont[0])
            volissue_root = lh.fromstring(volissue_str)
            raw_volissue = volissue_root.xpath('//p')[0]
            return self.clean_tags(raw_volissue)
        except:
            return ''
    
    
    # タイトルを生のhtmlからパースする
    def parse_title(self,root):
        title_cont = root.xpath('//h1[contains(@class,"'+self.title_class+'")]')
        try:
            title_str = lh.tostring(title_cont[0])
            title_root = lh.fromstring(title_str)
            return title_root.xpath('//h1')[0].text
        except:
            return ''
    
    # アブストを生のhtmlからパースする
    def parse_abstract(self,root):
        abstract_cont = root.xpath('//div[contains(@class,"'+self.abstract_class+'")]')
        try:
            abstract_str = lh.tostring(abstract_cont[0])
            abstract_root = lh.fromstring(abstract_str)
            raw_abstract = abstract_root.xpath('//p')[0]
            return self.clean_tags(raw_abstract)
        except:
            return ''
    # DOIをScriptタグからパースする
    def parse_doi(self,root):
        try:
            script_cont = self.get_script_info(root)
            script_raw_text = script_cont.text_content()
            del_prefix_text = script_raw_text.split(self.doi_variable,1)[-1]
            del_pre_suf_text = del_prefix_text.split(';',1)[0]
            munged_doi = del_pre_suf_text.strip('\'')
            return munged_doi
        except:
            return ''
    
    # volissueから年を引っ張る
    def parse_date(self,root):
        try:
            script_cont = self.get_script_info(root)
            script_raw_text = script_cont.text_content()
            del_prefix_text = script_raw_text.split(self.date_variable,1)[-1]
            del_pre_suf_text = del_prefix_text.split(';',1)[0]
            munged_date = del_pre_suf_text.strip('\'')
            return munged_date
        except:
            return ''
    
    # Scriptタグに埋まっている基本情報を取って返す
    def get_script_info(self,root):
        script_cont = root.xpath('//script')
        try:
            for one_script in script_cont:
                if 'SDM.pm.doi' in lh.tostring(one_script):
                    return one_script
        except:
            return ''
    
    # pタグに含まれているテキスト要素だけを返す
    def clean_tags(self,raw_p_element):
        return lh.tostring(raw_p_element,method="text",encoding="unicode")
    
    # 記号を抜いた単語だけを返す
    def get_token(self,target_string):
        word_tokenizer = rt(r'\w+')
        return word_tokenizer.tokenize(target_string)
    
    # 文字のbi-gramを作成して返す
    def get_char_bigram(self,raw_abstract):
        bigrams = filter(lambda b:b!="", [raw_abstract[k:k+2] for k in range(len(raw_abstract)-1)])
        return bigrams
    
    # 単語のbi-gramを作成して返す
    def get_word_bigram(self,raw_abstract):
        bigrams = filter(lambda b:b!="", [" ".join(raw_abstract[k:k+2]) for k in range(len(raw_abstract)-1)])
        return bigrams
    
    # ログをテキストファイルに出力する
    def logging(self,log_string):
        log_file = open(self.log_filepath,'a')
        log_file.writelines(log_string + '\n')
        log_file.close()

    # 現在時刻を文字列で返す
    def get_now(self):
        d = dt.datetime.today()
        return self.get_utf(str(d))
    
