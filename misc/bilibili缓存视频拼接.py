# �����ϲ��ض��ļ����µ���Ƶ�ļ���Ȼ�������ָ���ļ�����
# ��Ҫ����Ҫmoviepy�����
from moviepy.editor import *
import os
from natsort import natsorted
# natsort��һ��ʵ������Ŀ⣬���ܹ������ܡ�ʶ��Ҫ��������ݣ���ͼ���������Ͻ��з������������Ҫ��������ݺ���С���Ȼ������
import json

# psutil��һ����ƽ̨���ܹ�����ʵ�ֻ�ȡϵͳ���еĽ��̺�ϵͳ�����ʣ�����CPU���ڴ桢���̡�����ȣ���Ϣ������Ҫ������ϵͳ��أ����ܷ��������̹�����ʵ����ͬ�������й����ṩ�Ĺ��ܣ���ps��top��lsof��netstat
# ��ifconfig��who��df��kill��free��nice��ionice��iostat��iotop��uptime��pidof��tty��taskset��pmap�ȡ�Ŀǰ֧��32λ��64λ��Linux��Windows��OS
# X��FreeBSD��Sun Solaris�Ȳ���ϵͳ.
import psutil


# ɱ��moviepy�������ض�����
def killProcess():
    # ����python�����������г��ֵ��쳣�ʹ���
    try:
        # pids�����鿴ϵͳȫ������
        pids = psutil.pids()
        for pid in pids:
            # Process�����鿴��������
            p = psutil.Process(pid)
            # print('pid-%s,pname-%s' % (pid, p.name()))
            # ������
            if p.name() == 'ffmpeg-win64-v4.1.exe':
                # �ر����� /f��ǿ��ִ�У�/im��Ӧ������
                cmd = 'taskkill /f /im ffmpeg-win64-v4.1.exe  2>nul 1>null'
                # python����Shell�ű�ִ��cmd����
                os.system(cmd)
    except:
        pass


if __name__ == '__main__':
    # ѭ����
    for i in range(120):
        # ��ȡ��Ӧ��Ƶ�����json�ļ�·��
        myjsondirs = './video/{}/entry.json'.format(i + 1)
        # ����ƴ����ɺ���Ƶ�ı���
        vdtitle = ''
        with open(myjsondirs, 'r', encoding='UTF-8') as load_f:
            # loads������json��ʽ����ת��Ϊ�ֵ䣨��ȡ�ı��ô˷���
            load_dict = json.load(load_f)
            vdtitle = load_dict['page_data']['part']
        # ��Ƶ�ļ���·��
        mydirs = './video/{}/lua.flv.bili2api.80'.format(i + 1)
        # ����ƴ����Ƶ������
        L = []
        # ���� video �ļ���
        # rootָ���ǵ�ǰ���ڱ���������ļ��еı���ĵ�ַ��
        # dirs��һ�� list�������Ǹ��ļ��������е�Ŀ¼������(��������Ŀ¼)��
        # filesͬ���� list�������Ǹ��ļ��������е��ļ�(��������Ŀ¼)
        for root, dirs, files in os.walk(mydirs):
            # ���ļ�������
            # files.sort()
            # ��Ȼ����
            files = natsorted(files)
            # print(files)
            # ���������ļ�
            for file in files:
                # os.path.splitext(���ļ�·����)    �����ļ�������չ����Ĭ�Ϸ���(fname, fextension)Ԫ�飬������Ƭ����
                # �����׺��Ϊ .flv
                if os.path.splitext(file)[1] == '.flv':
                    # .blv��ʽ��Ƶ������·��
                    filePath = os.path.join(root, file)
                    # ��ȡ��Ƶ���ڴ�
                    myvideo = VideoFileClip(filePath)
                    # ��ӵ�����
                    L.append(myvideo)
        # �Զ����Ƶ��ʱ���Ͻ���ƴ��
        final_clip = concatenate_videoclips(L)
        targetdir = './target/{}.mp4'.format(vdtitle)
        # ��һ������Ŀ����Ƶ�ļ�����
        # final_clip.to_videofile(targetdir, fps=24)
        # ��������������Ŀ����Ƶ�ļ�����
        final_clip.write_videofile(targetdir, fps=24,
                                   remove_temp=True)
        # remove_temp=True��ʾ���ɵ���Ƶ�ļ�����ʱ��ŵģ���Ƶ���ɺ���Ƶ�ļ����Զ����������ΪFalse��ʾ����Ƶ�ļ���ͬʱ���ɣ�
        print("{}---{}---ƴ�ӳɹ���".format(i + 1, vdtitle))
        killProcess()
