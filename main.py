import time
import requests
import json
import os

s = requests.session()

username = ""
password = ""

record_list = []

suffixMap = {
    "C++": ".cpp",
    "Python3": ".py",
    "Python": ".py",
    "MySQL": ".sql",
    "Go": ".go",
    "Java": ".java",
    "C": ".c",
    "JavaScript": ".js",
    "PHP": ".php",
    "C#": ".cs",
    "Ruby": ".rb",
    "Swift": ".swift",
    "Scala": ".scl",
    "Kotlin": ".kt",
    "Rust": ".rs",
}


def read_config():
    with open("config.json", "r") as f:
        conf = json.load(f)
        global username, password
        username = conf["username"]
        password = conf["password"]


def login():
    s.post(
        "https://leetcode.cn/accounts/login/",
        data={"login": username, "password": password},
        headers={"Referer": "https://leetcode.cn/accounts/login/"},
    )


def fetch_list():
    cur_page = 1
    while True:
        print("获取范围 " + str(cur_page * 40 - 40) + "-" + str(cur_page * 40))
        res = s.get(
            "https://leetcode.cn/api/submissions/",
            params={"offset": (cur_page - 1) * 40, "limit": 40},
        ).json()
        if len(res["submissions_dump"]) == 0:
            print("结束")
            return
        global record_list
        record_list += res["submissions_dump"]
        cur_page = cur_page + 1
        time.sleep(1)


def fetch_record(record_id):
    post_data = {
        "operationName": "mySubmissionDetail",
        "variables": {"id": str(record_id)},
        "query": "query mySubmissionDetail($id: ID!) {\n  submissionDetail(submissionId: $id) {\n    id\n    code\n   "
        " runtime\n    memory\n    rawMemory\n    statusDisplay\n    timestamp\n    lang\n    "
        "passedTestCaseCnt\n    totalTestCaseCnt\n    sourceUrl\n    question {\n      titleSlug\n      "
        "title\n      translatedTitle\n      questionId\n      __typename\n    }\n    ... on "
        "GeneralSubmissionNode {\n      outputDetail {\n        codeOutput\n        expectedOutput\n        "
        "input\n        compileError\n        runtimeError\n        lastTestcase\n        __typename\n      "
        "}\n      __typename\n    }\n    submissionComment {\n      comment\n      flagType\n      "
        "__typename\n    }\n    __typename\n  }\n}\n",
    }
    res = s.post(
        "https://leetcode.cn/graphql/",
        data=json.dumps(post_data),
        headers={"Content-Type": "application/json"},
    ).json()
    return res["data"]["submissionDetail"]


def main():
    read_config()
    login()
    fetch_list()
    for i in record_list:
        r = fetch_record(i["id"])
        print(i)
        code_dir = os.path.join("out", r["question"]["questionId"])
        if not os.path.exists(code_dir):
            os.mkdir(code_dir)
        code_file = str(r["id"])
        code_file += "_" + str(r["statusDisplay"]).lower().replace(" ", "_")
        if str(r["statusDisplay"]) == "Accepted":
            code_file += "_" + str(r["runtime"]).replace(" ", "")
            code_file += "_" + str(r["rawMemory"])
        code_file += suffixMap[i["lang"]]
        with open(os.path.join(code_dir, code_file), "w") as f:
            f.write(r["code"])
        with open(os.path.join(code_dir, "record.json"), "w") as f:
            json.dump({"simple": i, "full": r}, f)
        time.sleep(1)


if __name__ == "__main__":
    main()
