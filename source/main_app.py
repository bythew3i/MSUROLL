
from tkinter import *
from tkinter import messagebox
import time
import threading
from splinter import Browser
import re
from urllib.request import urlopen

import sys # for debug purpose

# path for chromedriver
executable_path = {'executable_path':'/usr/local/bin/chromedriver'}
HEADLESS = True

class MSUROLLAPP(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("MSU Roll")
        self.resizable(False, False)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=50, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainPage, RollingPage):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="news")

        self.showFrame("MainPage")

        self.updateURL = "https://raw.githubusercontent.com/by-the-w3i/MSU_ROLL/master/VERSION"
        self.downloadURL = "https://github.com/by-the-w3i/MSU_ROLL/releases"
        self.version = "1.1"



    def showFrame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def checkUpdates(self):
        try:
            with urlopen(self.updateURL) as response:
                latest_version = response.read().decode('utf-8').strip()
                if self.version != latest_version:
                    messagebox.showinfo(
                        "Update",
                        "Current Version: {}\n\nThe latest version {} is out.\n\nPlease download from {}".format(self.version, latest_version, self.downloadURL)
                    )
                else:
                    messagebox.showinfo(
                        "Update",
                        "Current version is the latest one."
                    )
        except:
            messagebox.showwarning(
                "Internet Error",
                "The Internet is NOT CONNECTED."
            )




class MainPage(Frame):
    def __init__(self, master, controller):
        # all the courses targets
        self.targets = []

        Frame.__init__(self, master)
        self.controller = controller
        # self.pack(padx=50, pady=20)
        # self.master.geometry('{}x{}'.format(500, 300))
        # self.master.tk_setPalette(background='#545454')

        Label(self, text="MSU NetID:").grid(row=0, column=0, sticky=E)
        Label(self, text="PASSWORD:").grid(row=1, column=0, sticky=E)

        self.ID_entry = Entry(self)
        self.PW_entry = Entry(self, show="*")
        self.ID_entry.grid(row=0, column=1, columnspan=2, sticky=(E,W))
        self.PW_entry.grid(row=1, column=1, columnspan=2, sticky=(E,W))
        self.ID_entry.focus_set()

        Label(self, text="Year:").grid(row=2, column=0, sticky=E)
        self.year_entry = Entry(self, width=10)
        self.year_entry.insert(0,'2018')
        self.year_entry.grid(row=2, column=1)

        self.season = StringVar(self)
        self.season.set("Spring")
        OptionMenu(self, self.season, "Fall", "Spring", "Summer").grid(row=2,column=2)

        # Message(self, text="Seperate by a single space." ,fg='red', anchor=E, width=50).grid(row=3, columnspan=3)
        Label(self, text="Subject:").grid(row=3, column=0, sticky=E)
        self.sub_entry = Entry(self, width=10)
        self.sub_entry.insert(0,'CSE 415')
        self.sub_entry.grid(row=3, column=1, columnspan=2, sticky=(E,W))

        Label(self, text="Section:").grid(row=4, column=0, sticky=E)
        self.sec_entry = Entry(self, width=10)
        self.sec_entry.insert(0,'1')
        self.sec_entry.grid(row=4, column=1)

        Button(self, text="add to list", command=self.addCourse).grid(row=4, column=2, sticky=(E,W))

        self.courses = Listbox(self)
        self.courses.grid(row=5, column=0, columnspan=2)

        Button(self, text="delete", command=self.delCourse).grid(row=5, column=2, sticky=(E,W))

        Button(self, text="Start Rolling >>>", command=self.rolling).grid(row=6,columnspan=3, sticky=(E,W))
        Button(self, text="Check for updates", command=lambda:self.controller.checkUpdates()).grid(row=7,columnspan=3, sticky=(E,W))


    def authentication(self, ID, PW):
        try:
            b = Browser('chrome', headless=HEADLESS, **executable_path)
            URL = "https://schedule.msu.edu/Login.aspx"
            b.visit(URL)
            b.find_by_id("netid").fill(ID)
            b.find_by_id("pswd").fill(PW)
            b.find_by_value("Login").click()
            url = b.url
            b.quit()
            if url == "https://login.msu.edu/Login":
                return False
            return True
        except:
            # messagebox.showwarning(
            #     "System Error",
            #     "Error: chromedriver not found!!!"
            # )
            messagebox.showwarning(
                "System Error",
                "Error:{}\n{}".format(sys.exc_info()[0], sys.exc_info()[1])
            )

    def addCourse(self):
        course_lst = [s.strip() for s in self.sub_entry.get().strip().split()]
        course = "{} {}".format(course_lst[0],course_lst[1]).upper()
        year = self.year_entry.get().strip()
        section = self.sec_entry.get().strip()
        if not year.isdigit():
            messagebox.showwarning(
                "Add Error",
                "Year: Please input a valid year! (make sure there is no space)"
            )
        elif len(course_lst) != 2:
            messagebox.showwarning(
                "Add Error",
                "Subject should be separated by a space. Format should be 'CSE 415'or 'IAH 241A'"
            )

        elif not section.isdigit():
            messagebox.showwarning(
                "Add Error",
                "Section: Please input a valid integer in Section! (make sure there is no space)"
            )

        else:
            info = "{} {} {} sec{}".format(year,self.season.get(), course, int(section))
            if info not in self.targets:
                self.targets.append(info)
                self.courses.insert(END, info)
            else:
                messagebox.showwarning(
                    "Add Error",
                    "Duplicate: {}".format(info)
                )



    def delCourse(self):
        to_del = self.courses.curselection()
        if len(to_del)==0 :
            messagebox.showwarning(
                "Delete Error",
                "No active course is selected ..."
            )
        else:
            ind = to_del[0]
            self.targets.remove(self.courses.get(ind))
            self.courses.delete(ind)


    def rolling(self):
        if len(self.targets)==0:
            messagebox.showwarning(
                "Error",
                "No class in the list. Please click 'add to list'."
            )
        elif self.ID_entry.get()=="" or self.PW_entry.get()=="":
            messagebox.showwarning(
                "Error",
                "NETID and PASSWORD can not be empty."
            )
            if self.ID_entry.get()=="":
                self.ID_entry.focus_set()
            else:
                self.PW_entry.focus_set()
        elif not self.authentication(self.ID_entry.get(), self.PW_entry.get()):
            messagebox.showwarning(
                "Error",
                "NETID and PASSWORD are not right."
            )
            self.ID_entry.focus_set()
        else:
            understand = messagebox.askyesno(
                "Something you should know",
                "I understand that MSU Rolling works only when my computer is on."
            )
            if understand:
                self.controller.showFrame("RollingPage")
                self.controller.frames["RollingPage"].start_thread()
                # print("rollings")
            else:
                donate = messagebox.askyesno(
                    "Why I can not use MSU Roll offline?",
'''Two reasons:
<1> The APP developper wants to keep user's NetID and PASSWORD locally. It is unsafe to upload user's info online.
<2> The APP developper is soooo POOR. He can not afford a server for this App.

If you want to see some features in the future:
a) offline enrolling (without keeping computer turning on)
b) SMS notification
c) Mobile App
etc ...

You are very welcome to DONATE this developper by clicking [Yes]
"YES, Anything Helps."
''')
                if donate:
                    messagebox.showinfo(
                        "Donate",
                        "WECHAT PAY: 351425189\n\nCHASE Quickpay:\n jevin0change@gmail.com"
                    )

class RollingPage(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller


        Button(self, text="FAQs",command=self.faqs).pack()
        label = Label(self, text="Enrolling class for you ...")
        label.pack(side="top", fill="x", pady=10)
        button = Button(self, text="STOP Rolling and Quit",
                        command=lambda:controller.destroy())
        button.pack()


        Button(self, text="Live Status:",command=self.liveStatus).pack(pady=(10,0))
        self.msg = Message(self, text="Validating class list ...", width=500, fg="#25a5e4")
        self.msg.pack()

        self.status_table = {}
        self.ready_table = {}


    def start_thread(self):
        thread = threading.Thread(target=self.looping, args=())
        thread.daemon = True
        thread.start()

    def faqs(self):
        messagebox.showwarning(
            "FAQs",
            ">> ISSUES:\nIf you CLOSE THIS PROGRAM, DISCONNECT TO INTERNET or CLOSE THE COMPUTER, the Enrolling will fail. You may need to start over again. However feel free to minimize this window when it is running.\n\n>> BUG REPORT:\nWECHAT: 351425189"
        )

    def liveStatus(self):
        messagebox.showwarning(
            "Live Status",
            "[ERROR]\nThis class is not found.\n\n[READY]\nThis class is ready to enroll anythime when someone drops it.\n\n[ENROLLED]\nCongratulations!!! You Successfully enrolled this class.\n\n[FAILED]\nEnroll failed due to permission denied. (You may not have the right to enroll this class or You have already enrolled this class)"
        )

    def updateStatus(self, cls_lst, finish=False):
        clor = "#25a5e4"
        msg = ""
        for c in cls_lst:
            if c in self.status_table:
                msg += "[{}] {}\n".format(self.status_table[c], c)
            else:
                break
        if finish:
            msg += "\nROLLING FINISHED!!!\nPlease check your msu schedule."
            clor = "red"
        self.msg.configure(text=msg, fg=clor)

    def updateReady(self, contents):
        for k in self.ready_table:
            c = self.ready_table[k][1]
            plan_idx = re.findall('<a id="(.+)?" title="Enroll in {}"'.format(c), contents)[0][-1]
            self.ready_table[k][0] = plan_idx


    def checkLogin(self, b_lst, url_plan, ID, PW):
        if b_lst[0].url != url_plan:
            b_lst[0].find_by_id("netid").fill(ID)
            b_lst[0].find_by_id("pswd").fill(PW)
            b_lst[0].find_by_value("Login").click()


    def looping(self):
        NETID = self.controller.frames["MainPage"].ID_entry.get()
        PASSWD = self.controller.frames["MainPage"].PW_entry.get()
        CLS_LST = self.controller.frames["MainPage"].targets

        URL = "https://schedule.msu.edu"
        URL_PLAN = "https://schedule.msu.edu/Planner.aspx"

        b = Browser('chrome', headless=HEADLESS, **executable_path)
        for course in CLS_LST:
            tar = course.split()
            TERM = "{} {}".format(tar[1], tar[0])
            SUB = tar[2]
            SUB_NUM = tar[3]
            SEC = "{:03}".format(int(tar[4][3:]))

            try:
                # put all the list class in to user account planner
                b.visit(URL)
                term = b.find_by_text(TERM).value
                b.find_by_id("MainContent_SrearchUC_ddlTerm").select(term)
                b.find_by_id("MainContent_SrearchUC_ddlSubject").select(SUB)
                b.find_by_id("MainContent_SrearchUC_txtCourseNumber").fill(SUB_NUM)
                b.find_by_id("MainContent_SrearchUC_btnSubmit").click()
                combo = "{} {} Section {}".format(SUB, SUB_NUM, SEC)
                link = re.findall('<a href="(.+)?" title="[^"]+add {} to your planner"?>'.format(combo), b.html)[0]

                b.click_link_by_href(link)
                self.checkLogin([b], URL_PLAN, NETID, PASSWD)

                self.status_table[course] = "READY"
                self.ready_table[course] = ["-1", combo]
            except:
                # print("Error:", sys.exc_info()[0])
                self.status_table[course] = "ERROR"

            self.updateStatus(CLS_LST)

        # now go to the planner
        b.visit(URL_PLAN)
        self.checkLogin([b], URL_PLAN, NETID, PASSWD)
        # find the plan idx
        self.updateReady(b.html)
        # print(self.ready_table)


        STATUS_CODE = "MainContent_UCPlanned_rptPlanner_tdStatus_"
        ENROLL_CODE = "MainContent_UCPlanned_rptPlanner_imgEnroll_"
        CONTINUE_CODE ="MainContent_btnContinue"
        to_delete = None
        # looping arround
        while len(self.ready_table) > 0:
            b.visit(URL_PLAN)
            self.checkLogin([b], URL_PLAN, NETID, PASSWD)
            for course in self.ready_table:
                plan_idx = self.ready_table[course][0]
                combo = self.ready_table[course][1]
                # print(b.find_by_id(STATUS_CODE+plan_idx).text)
                if "Open" in b.find_by_id(STATUS_CODE+plan_idx).text:
                    # section open!! enroll the class
                    b.find_by_id(ENROLL_CODE+plan_idx).click()
                    b.find_by_id(CONTINUE_CODE).click()
                    if b.html.find("The course has been added to your schedule.")!=-1:
                        # enroll successfully
                        self.status_table[course] = "ENROLLED"
                    else:
                        # FAILED
                        self.status_table[course] = "FAILED"
                    to_delete = course
                    self.updateStatus(CLS_LST)
                    break

            if to_delete != None:
                b.visit(URL_PLAN)
                self.checkLogin([b], URL_PLAN, NETID, PASSWD)
                del self.ready_table[to_delete]
                self.updateReady(b.html)
                to_delete = None
            else:
                time.sleep(1) # sleep 1 second

        self.updateStatus(CLS_LST, True)

        b.quit()
        # print("Exit Looping")





if __name__ == "__main__":
    root = MSUROLLAPP()
    root.mainloop()
