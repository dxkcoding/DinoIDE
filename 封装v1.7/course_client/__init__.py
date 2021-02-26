from tkinter import ttk
import threading, tkinter as tk, os, json, functools, re
from tkinter.messagebox import showerror, showinfo
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from thonny.code import Editor
from thonny.config_ui import ConfigurationPage
from thonny import get_workbench
from functools import partial


class TerminalConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(
            self, text="服务器地址:", anchor="w").grid(
                row=0, column=0, sticky="w")
        self.add_entry("pyedu.server", row=0, column=1, width=20, padx=5)
        ttk.Label(self, text="端口:", anchor="w").grid(row=0, column=2)
        self.add_entry("pyedu.port", row=0, column=3, width=5, padx=5)


class UUIDHook(ttk.Frame):
    @property
    def base_url(self):
        wb = get_workbench()
        return f'http://{wb.get_option("pyedu.server")}:{wb.get_option("pyedu.port")}/p/thonny/'

    def __init__(self, master):
        """ 控件布局 """
        super().__init__(master)
        ttk.Label(self, text='当前UUID:').grid(sticky='w')
        self.uuid_var = tk.StringVar(self)
        self.uuid_input = ttk.Entry(self, width=64, textvariable=self.uuid_var)
        self.uuid_input.grid()

        frame_btn = ttk.Frame(self)
        frame_btn.grid(sticky='w')
        self.buttons = [
            ttk.Button(frame_btn, text='下载代码', command=self.load),
            ttk.Button(
                frame_btn,
                text='粘贴并下载代码',
                command=functools.partial(self.load, paste=1),
                width=14),
            ttk.Button(frame_btn, text='上传当前代码', command=self.save, width=12),
        ]
        for i, btn in enumerate(self.buttons):
            btn.grid(row=0, column=i)

        ttk.Label(self, text='注: 读取代码时需在上方输入UUID').grid(sticky='w')
        ttk.Label(self, text='代码文本第一行为自动生成内容').grid(sticky='w')
        ttk.Label(self, text='修改后将保存为新副本').grid(sticky='w')

        self.data = self.data_sent = None
        self.status = 0
        self.panel = get_workbench().get_editor_notebook()

    def _request(self, url, data=None):
        """ 远程发送请求并存储结果 """
        self.status = 1
        self.data = None
        self.data_sent = data
        try:
            if data:
                data = urlencode(data).encode('utf-8')
            # showinfo(message=data)
            req = urlopen(url, data)
            res = req.read().decode('utf-8')
            self.data = json.loads(res)
            self.status = 2
        except Exception as e:
            self.data = e
            self.status = 0
            raise

    def _checker(self, func_success=None, func_fail=None):
        """ 检查网络请求，执行回调 """

        def checker():
            if self.status == 0:
                if func_fail:
                    func_fail()
                else:
                    showerror('加载失败', self.data)
            elif self.status == 2:
                if func_success:
                    func_success()
                else:
                    showinfo('加载成功', self.data)
            else:
                self.after(100, checker)
                return

            for btn in self.buttons:
                btn['state'] = 'active'

        self.status = 1
        for btn in self.buttons:
            btn['state'] = 'disabled'
        self.after(100, checker)

    def _pick_uuid(self, code_raw: str):
        """ 获取代码文本中的UUID并分割返回 """
        tmp = code_raw.split('\n', 1)

        # 判断UUID开头
        uid_header = tmp[0].strip()
        is_header = False
        if (uid_header.startswith('#uuid#')
                or uid_header.startswith('#uuid_share#')
            ) and uid_header.endswith('#'):
            uid = uid_header[uid_header.index('#', 1) + 1:-1].strip()
            is_header = True
        else:
            uid = ''

        # 返回UID与剩余代码
        code = tmp[-1]
        if is_header:
            code = '' if len(tmp) == 1 else tmp[1]
        else:
            code = code_raw
        return uid, code

    def _attach_uuid(self, code, uuid):
        """ 在代码开头附着UUID """
        return '#uuid#  %s  #\n%s' % (uuid, code)

    def load(self, paste=False):
        """ 读取代码 """
        if paste:
            raw = self.clipboard_get().lower()
            tmp = re.search(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                raw)
            if tmp:
                self.uuid_var.set(raw[slice(*tmp.span())])
            else:
                return showerror('加载失败', '剪贴板中未找到有效的UUID')
        url = f'{self.base_url}read/?uuid={self.uuid_var.get().strip()}'
        threading.Thread(target=self._request, args=(url, )).start()
        self._checker(self._load_success)

    def save(self):
        """ 上传代码 """
        url = f'{self.base_url}upload/'

        # 读取UUID信息
        code_pool = self.panel.get_current_child()
        code_raw = code_pool._code_view.get_content()
        uid, code = self._pick_uuid(code_raw)
        content = self._attach_uuid(code, uid)

        # 保存请求
        data = {
            'file': content,
            'id': uid,
        }
        tmp = code_pool.get_filename()
        if tmp:
            tmp = os.path.basename(tmp)
            data['title'] = tmp

        threading.Thread(target=self._request, args=(url, data)).start()
        self._checker(self._save_success)

    def _load_success(self):
        """ 读取成功回调 """
        data = self.data

        # 成功加载
        if data['status'] == 1:
            # 在代码首行附着UUID
            content = data['file']
            uid, code = self._pick_uuid(content)
            content = self._attach_uuid(code, data['id'])

            # 加载代码至工作区
            editor = Editor(self.panel)
            # editor._filename = data['name']
            # tmp, editor.get_filename = editor.get_filename, lambda *a, **kw: data['name']
            self.panel.add(editor, text=data['name'])
            self.panel.select(editor)
            editor.focus_set()

            editor._code_view.set_content(content)
            editor._code_view.focus_set()
            editor._code_view.text.edit_modified(True)

            info = 'UUID: %s\n标题: %s\n作者: %s' % (
                data['id'],
                data['name'],
                data.get('user', '无'),
            )

            showinfo('加载成功', info)
            # editor.get_filename = tmp

        # 失败加载
        else:
            showerror('加载失败', data['fail'])

    def _save_success(self):
        """ 保存成功回调 """
        data = self.data

        # 成功保存
        if data['status'] == 1:
            info = 'UUID: %s\n标题: %s\n作者: %s' % (
                data['id'],
                data['name'],
                data.get('user', '无'),
            )

            # 新建保存时更新首行
            if data['id'] != self.data_sent['id']:
                uid, code = self._pick_uuid(self.data_sent['file'])
                content = self._attach_uuid(code, data['id'])

                # 更新窗口内容
                self.uuid_var.set(data['id'])
                self.panel.get_current_child()._code_view.set_content(content)

            showinfo('保存成功', info)

        # 失败保存
        else:
            showerror('保存失败', data['fail'])


def load_plugin():
    wb = get_workbench()
    wb.set_default("pyedu.server", '127.0.0.1')
    wb.set_default("pyedu.port", 80)
    wb.add_configuration_page("教学平台", TerminalConfigurationPage)
    wb.add_view(UUIDHook, 'Python学习面板', 'se')