import json
import os
import zipfile
from pathlib import Path


def convertDictToFiles(data, rootPath):
    def formatRecord(records, _rootPath):
        # 实时让分 真实分差 时间 有效性
        _rootPath.mkdir(exist_ok=True, parents=True)

        def formatter(_records, records_ji, output_fileName, sep_time=12, isEffect=1):
            from pandas import DataFrame
            # 实时让分 真实分差 时间 有效性
            parts = [[_records[0]]]
            for i in _records[1:]:
                last_elm = parts[-1][-1]  # 选择该节中最后一个元素
                if last_elm[0].strip().split()[0] == i[0].strip().split()[0]:
                    parts[-1].append(i)
                else:
                    parts.append([i])
            result_arr = []
            for i, part in enumerate(parts):
                start = i * 12 * 60
                for t, score, letScore in part:
                    if len(t.strip().split()) < 2:
                        continue
                    t = list(map(lambda x: int(x), t.strip().split()[1].split(":")))
                    seconds = t[0] * 60 + t[1]
                    currentTime = start + (sep_time * 60 - seconds)
                    letScore = float(letScore)
                    result_arr.append([letScore, eval(score), currentTime, isEffect])
            length = len(result_arr)
            length_ji = len(records_ji)
            if length_ji > length:
                result_arr.extend([[None, None, None] for i in range(length_ji - length)])
            else:
                records_ji.extend([0 for i in range(length - length_ji)])
            result_arr2 = []
            for res, _ in zip(result_arr, records_ji):
                temp = [_]
                temp.extend(res)
                result_arr2.append(temp)
            df = DataFrame(result_arr2, columns=["即", "滚盘", "真实分差", "时间", "结果"])
            df.to_csv(f"{output_fileName}", index=False)

        for i, record in enumerate(records):
            i = str(i)
            formatter(record["records"], record["records_ji"], _rootPath / i)

    print(data)
    for k, v in data.items():
        stage = f"第{int(k) + 1}档"
        print(stage, "stage")
        root = rootPath / stage
        root.mkdir(exist_ok=True)
        [download_records, calc_index] = v["download_records"]
        (root / "info").write_text(f"{calc_index}")
        for i, records in enumerate(download_records):
            currentRoot = root / f"{i}"
            valid_records = records["valid_records"]  # 所有有效记录列表
            invalid_records = records["invalid_records"]
            valid_records_path = currentRoot / "数据集1"
            invalid_records_path = currentRoot / "数据集2"
            formatRecord(valid_records, valid_records_path)
            formatRecord(invalid_records, invalid_records_path)


def convert(data, packRoot):
    # packRoot = Path("zips")
    # packRoot.mkdir(exist_ok=True)
    # data = analysis_matches_by_name(obj.matchName, dateRange, obj.q, (obj.range.min, obj.range.max))
    inc_table = data["inc_table"]
    des_table = data["des_table"]
    matchNames = data["matchNames"]
    matchNames.sort()
    matchNames = "-".join(matchNames)
    zipFolder = packRoot / matchNames
    incFolder = zipFolder / "增量"
    desFolder = zipFolder / "减量"
    incFolder.mkdir(parents=True, exist_ok=True)
    desFolder.mkdir(parents=True, exist_ok=True)
    convertDictToFiles(inc_table, incFolder)
    convertDictToFiles(des_table, desFolder)


def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    dirpath = dirpath.__str__()
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')

        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()
