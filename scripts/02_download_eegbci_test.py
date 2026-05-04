from mne.datasets import eegbci

# EEGBCI 데이터셋에서 1번 피험자를 선택한다
subject = 1

# 1번 run과 2번 run을 선택한다
# run 1 = baseline eyes open
# run 2 = baseline eyes closed
runs = [1, 2]

# MNE가 EEGBCI 데이터셋에서 subject 1의 run 1, 2 파일을 다운로드하거나, 
# 이미 다운로드되어 있으면 그 파일 위치를 찾아준다
file_paths = eegbci.load_data(subject, runs)

# 아래부터는 다운로드된 파일 위치를 화면에 출력하는 부분
print("Downloaded / located files:")

# file_paths 안에 들어 있는 파일 경로를 하나씩 꺼내서 출력한다 
for path in file_paths:
    print(path)