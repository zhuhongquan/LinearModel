import numpy as np
import datetime
import random


class DataSet():
    def __init__(self, filename):
        self.filename = filename
        self.sentences = []
        self.tags = []
        sentence = []
        tag = []
        word_num = 0
        file = open(filename, encoding='utf-8')
        while True:
            line = file.readline()
            if not line:
                break
            if line == '\n':
                self.sentences.append(sentence)  # [[word1,word2,...],[word1...],[...]]
                self.tags.append(tag)  # [[tag1,tag2,...],[tag1...],[...]]
                sentence = []
                tag = []
            else:
                sentence.append(line.split()[1])  # [word1,word2,...]
                tag.append(line.split()[3])  # [tag1,tag2,...]
                word_num += 1
        self.sentences_num = len(self.sentences)  # 统计句子个数
        self.word_num = word_num  # 统计词语个数

        print('{}:共{}个句子,共{}个词。'.format(filename, self.sentences_num, self.word_num))
        file.close()

    def split(self):
        data = []
        for i in range(len(self.sentences)):
            for j in range(len(self.sentences[i])):
                data.append((self.sentences[i], j, self.tags[i][j]))  # [(句子1,词1,词性),(句子1,词2,词性)...]
        return data


class LinearModel(object):
    def __init__(self, train_file, dev_file, test_file):
        self.train_data = DataSet(train_file)
        self.dev_data = DataSet(dev_file)
        self.test_data = DataSet(test_file)
        self.features = {}
        self.weights = []
        self.v = []
        self.tag_dict = {}
        self.tag_list = []

    def create_feature_template(self, sentence, position):
        template = []
        cur_word = sentence[position]
        cur_word_first_char = cur_word[0]
        cur_word_last_char = cur_word[-1]
        if position == 0:
            last_word = '##'
            last_word_last_char = '#'
        else:
            last_word = sentence[position - 1]
            last_word_last_char = sentence[position - 1][-1]

        if position == len(sentence) - 1:
            next_word = '$$'
            next_word_first_char = '$'
        else:
            next_word = sentence[position + 1]
            next_word_first_char = sentence[position + 1][0]

        template.append('02:' + cur_word)
        template.append('03:' + last_word)
        template.append('04:' + next_word)
        template.append('05:' + cur_word + '*' + last_word_last_char)
        template.append('06:' + cur_word + '*' + next_word_first_char)
        template.append('07:' + cur_word_first_char)
        template.append('08:' + cur_word_last_char)

        for i in range(1, len(sentence[position]) - 1):
            template.append('09:' + sentence[position][i])
            template.append('10:' + sentence[position][0] + '*' + sentence[position][i])  # 第一个字符和当前字符添加到模板中
            template.append('11:' + sentence[position][-1] + '*' + sentence[position][i])  # 最后一个字符和当前字符添加到模板中

        if len(sentence[position]) == 1:  # 如果当前分词只有一个字符
            template.append('12:' + cur_word + '*' + last_word_last_char + '*' + next_word_first_char)

        for i in range(0, len(sentence[position]) - 1):
            if sentence[position][i] == sentence[position][i + 1]:  # 如果当前字符和下一个字符相等
                template.append('13:' + sentence[position][i] + '*' + 'consecutive')

        for i in range(0, 4):
            if i > len(sentence[position]) - 1:
                break
            template.append('14:' + sentence[position][0:i + 1])
            template.append('15:' + sentence[position][-(i + 1)::])

        return template

    def create_feature_space(self):
        for i in range(len(self.train_data.sentences)):
            sentence = self.train_data.sentences[i]
            tags = self.train_data.tags[i]
            for j in range(len(sentence)):
                template = self.create_feature_template(sentence, j)
                for f in template:  # 对特征进行遍历
                    if f not in self.features.keys():  # 如果特征不在特征字典中，则添加进去
                        self.features[f] = len(self.features)  # 给该特征一个独立的序号标记
                for tag in tags:
                    if tag not in self.tag_list:
                        self.tag_list.append(tag)
        self.tag_list = sorted(self.tag_list)
        self.tag_dict = {t: i for i, t in enumerate(self.tag_list)}
        self.weights = [0] * (len(self.features) * len(self.tag_dict))
        self.v = [0] * (len(self.features) * len(self.tag_dict))
        self.update_times = [0] * (len(self.features) * len(self.tag_dict))
        print("the total number of features is {}".format(len(self.features)))

    def dot(self, feature_id, tag, averaged=False):
        score = 0
        offset = self.tag_dict[tag] * len(self.features)
        for f_id in feature_id:
            if averaged:
                score += self.v[f_id + offset]
            else:
                score += self.weights[f_id + offset]
        return score

    def get_max_tag(self, sentence, position, averaged=False):
        template = self.create_feature_template(sentence, position)
        f_id = [self.features[f] for f in template if f in self.features]
        tag_id = np.argmax([self.dot(f_id, tag, averaged) for tag in self.tag_list])
        return self.tag_list[tag_id]

    def save(self, path):
        f = open(path, 'w', encoding='utf-8')
        for tag, id in self.tag_dict.items():
            offset = id * len(self.features)
            for feature, feature_id in self.features.items():
                f.write(feature[0:3] + tag + '*' + feature[3:] + '\t' + str(self.weights[offset + feature_id]) + '\n')
        f.close()

    def evaluate(self, data, averaged=False):
        total_num = 0
        correct_num = 0
        for i in range(len(data.sentences)):
            sentence = data.sentences[i]
            tags = data.tags[i]
            total_num += len(tags)
            for j in range(len(sentence)):
                predict_tag = self.get_max_tag(sentence, j, averaged)
                if predict_tag == tags[j]:
                    correct_num += 1

        return correct_num, total_num, correct_num / total_num

    def update_v(self, index, update_time, last_w_value):
        last_update_time = self.update_times[index]  # 上一次更新所在的次数
        current_update_time = update_time  # 本次更新所在的次数
        self.update_times[index] = update_time
        self.v[index] += (current_update_time - last_update_time - 1) * last_w_value + self.weights[index]

    def online_train(self, iterator=20, averaged=False, shuffle=True, exitor=20):
        max_dev_precision = 0.0
        max_iterator = -1
        update_time = 0
        counter = 0
        data = self.train_data.split()
        if averaged:
            print('using V to predict dev data...')
        for iter in range(iterator):
            print('iterator: %d' % (iter))
            starttime = datetime.datetime.now()
            if shuffle:
                random.shuffle(data)
                print('\tshuffle the train data...')

            for i in range(len(data)):
                sentence = data[i][0]
                j = data[i][1]
                gold_tag = data[i][2]
                predict_tag = self.get_max_tag(sentence, j, False)
                if predict_tag != gold_tag:
                    update_time += 1
                    feature = self.create_feature_template(sentence, j)
                    offset_predict_tag = self.tag_dict[predict_tag] * len(self.features)
                    offset_gold_tag = self.tag_dict[gold_tag] * len(self.features)

                    for f in feature:
                        if f in self.features.keys():
                            index = self.features[f] + offset_predict_tag
                            last_w_value = self.weights[index]
                            self.weights[index] -= 1
                            self.update_v(index, update_time, last_w_value)

                            index = self.features[f] + offset_gold_tag
                            last_w_value = self.weights[index]
                            self.weights[index] += 1
                            self.update_v(index, update_time, last_w_value)

            # 本次迭代完成
            current_update_times = update_time  # 本次更新所在的次数
            for i in range(len(self.v)):
                last_w_value = self.weights[i]
                last_update_times = self.update_times[i]  # 上一次更新所在的次数
                if current_update_times != last_update_times:
                    self.update_times[i] = current_update_times
                    self.v[i] += (current_update_times - last_update_times - 1) * last_w_value + self.weights[i]

            train_correct_num, total_num, train_precision = self.evaluate(self.train_data, False)
            print('\t' + 'train准确率：{} / {} = {}'.format(train_correct_num, total_num, train_precision))
            dev_correct_num, dev_num, dev_precision = self.evaluate(self.dev_data, averaged)
            print('\t' + 'dev准确率：{} / {}= {}'.format(dev_correct_num, dev_num, dev_precision))

            if self.test_data != None:
                test_correct_num, test_num, test_precision = self.evaluate(self.test_data, averaged)
                print('\t' + 'test准确率：{} / {} = {}'.format(test_correct_num, test_num, test_precision))

            if dev_precision > max_dev_precision:
                max_dev_precision = dev_precision
                max_iterator = iter
                counter = 0
            else:
                counter += 1
                # self.save('./result.txt')
            endtime = datetime.datetime.now()
            print("\titeration executing time is " + str((endtime - starttime)) + " s")

            if train_correct_num == total_num:
                break

            if counter >= exitor:
                break
        print('iterator = %d , max_dev_precision = %f' % (max_iterator, max_dev_precision))


if __name__ == '__main__':
    train_data_file = 'data/train.conll'  # 训练集文件
    dev_data_file = 'data/dev.conll'  # 开发集文件
    test_data_file = 'data/test.conll'  # 测试集文件
    averaged = False  # 是否使用averaged percetron
    iterator = 100  # 最大迭代次数
    shuffle = True  # 每次迭代是否打乱数据
    exitor = 10  # 连续多少次迭代没有提升效果就退出

    starttime = datetime.datetime.now()
    lm = LinearModel(train_data_file, dev_data_file, test_data_file)
    lm.create_feature_space()
    lm.online_train(iterator, averaged, shuffle, exitor)
    end_time = datetime.datetime.now()
    print("executing time is " + str((end_time - starttime).seconds) + " s")
