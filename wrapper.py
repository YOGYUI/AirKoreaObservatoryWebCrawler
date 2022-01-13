import requests
import datetime
import pandas as pd
from typing import Union
from bs4 import BeautifulSoup, element


class AirQuality:
    def __init__(self):
        api_key_utf8 = "SV5xOdOCXxDs5yZxOsanMwoY9Jeht7UPM%2BnKqBY3tFIpAivokjm4XMm7Dr9QvXMgWXdwkxIeFRDHpgQaSQtmig%3D%3D"
        self._api_key = requests.utils.unquote(api_key_utf8, encoding='utf-8')
        self._url_base = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc"
    
    @staticmethod
    def _convert_tag_string(item_: element.Tag, key_: str):
        try:
            return item_.find(key_.lower()).text.strip()
        except AttributeError:
            return None
    
    def _getDataFrameCommon(self, service_url: str, params: dict, parse_info: dict, change_header_name: bool = True) -> pd.DataFrame:
        """
        response - xml - dataframe 변환 공통 메서드
        """
        url = self._url_base + "/" + service_url
        params['serviceKey'] = self._api_key
        params['returnType'] = "xml"
        params['numOfRows'] = 999999
        
        print(f"Try to request service - {service_url}")
        response = requests.get(url, params=params)
        print(f"GET Response Status: {response.status_code}")
        if response.status_code == 200:
            xml = BeautifulSoup(response.text, "lxml")
            resultcode = xml.find("resultcode").text
            resultmsg = xml.find("resultmsg").text
            print(f"Result: {resultmsg}({resultcode})")
            totalcount = int(xml.find("totalcount").text)
            print(f"Total Count: {totalcount}")
            items = xml.findAll("item")
            item_list = []
            for item in items:
                # 파싱되지 않는 태그 있는지 여부 검색 후 출력
                tag_names = [x.name for x in list(item)]
                keys = [x.lower() for x in parse_info.keys()]
                unparsed = list(filter(lambda x: x not in keys and x is not None, tag_names))
                if len(unparsed) > 0:
                    print(f"Warning: parse info missing - {unparsed}")
                # 딕셔너리로 파싱
                item_dict = {}
                for key, value in parse_info.items():
                    if change_header_name:
                        item_dict[value] = self._convert_tag_string(item, key)
                    else:
                        item_dict[key] = self._convert_tag_string(item, key)
                item_list.append(item_dict)
            return pd.DataFrame(item_list)
        else:
            return pd.DataFrame()
    
    def getAirQualityPrediction(self, target_date: Union[datetime.date, str] = None, change_header_name: bool = True) -> pd.DataFrame:
        """
        대기질 예보통보 조회
        """
        if target_date is None:
            search_date = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            if isinstance(target_date, datetime.date):
                search_date = target_date.strftime("%Y-%m-%d")
            else:
                search_date = str(target_date)
        params = {
            "searchDate": search_date,
            "ver": "1.1"
        }
        parser_info = {
            "dataTime": "통보시간",
            "informCode": "통보코드",
            "informOverall": "예보개황",
            "informCause": "발생원인",
            "informGrade": "예보등급",
            "actionKnack": "행동요령",
            "imageUrl1": "첨부파일명1",
            "imageUrl2": "첨부파일명2",
            "imageUrl3": "첨부파일명3",
            "imageUrl4": "첨부파일명4",
            "imageUrl5": "첨부파일명5",
            "imageUrl6": "첨부파일명6",
            "imageUrl7": "첨부파일명7",
            "imageUrl8": "첨부파일명8",
            "imageUrl9": "첨부파일명9",
            "informData": "예측통보시간"
        }
        return self._getDataFrameCommon('getMinuDustFrcstDspth', params, parser_info, change_header_name)

    def getCurrentBadAirObservatoryInfo(self, change_header_name: bool = True):
        """
        통합대기환경지수 나쁨 이상 측정소 목록 조회
        """
        params = {}
        parser_info = {
            "stationName": "측정소명",
            "addr": "측정소 주소",
        }
        return self._getDataFrameCommon('getUnityAirEnvrnIdexSnstiveAboveMsrstnList', params, parser_info, change_header_name)
    
    def getWeeklyDustPredict(self, target_date: Union[datetime.date, str] = None, change_header_name: bool = True) -> pd.DataFrame:
        """
        초미세먼지 주간예보 조회
        """
        if target_date is None:
            search_date = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            if isinstance(target_date, datetime.date):
                search_date = target_date.strftime("%Y-%m-%d")
            else:
                search_date = str(target_date)
        params = {
            "searchDate": search_date
        }
        parser_info = {
            "frcstOneCn": "첫째날예보",
            "frcstTwoCn": "둘째날예보",
            "frcstThreeCn": "셋째날예보",
            "frcstFourCn": "넷째날예보",
            "presnatnDt": "발표일시",
            "frcstOneDt": "첫째날예보일시",
            "frcstTwoDt": "둘째날예보일시",
            "frcstThreeDt": "셋째날예보일시",
            "frcstFourDt": "넷째날예보일시",
            "gwthcnd": "대기질 전망"
        }
        return self._getDataFrameCommon('getMinuDustWeekFrcstDspth', params, parser_info, change_header_name)
        
    def getObservatoryMeasurement(self, obs_name: str, duration_day: int = 1, change_header_name: bool = True):
        """
        측정소별 실시간 측정정보 조회
        """
        if duration_day < 2:            
            dataTerm = "DAILY"
        elif duration_day <= 31:
            dataTerm = "MONTH"
        else:
            dataTerm = "3MONTH"
        params = {
            "stationName": obs_name,
            "dataTerm": dataTerm,
            "ver": "1.3"
        }
        parser_info = {
            "dataTime": "측정일",
            "mangName": "측정망 정보",
            "so2Value": "아황산가스 농도",
            "coValue": "일산화탄소 농도",
            "o3Value": "오존 농도",
            "no2Value": "이산화질소 농도",
            "pm10Value": "미세먼지(PM10) 농도",
            "pm10Value24": "미세먼지(PM10) 24시간 예측이동농도",
            "pm25Value": "초미세먼지(PM2.5) 농도",
            "pm25Value24": "초미세먼지(PM2.5) 24시간 예측이동농도",
            "khaiValue": "통합대기환경수치",
            "khaiGrade": "통합대기환경지수",
            "so2Grade": "아황산가스 지수",
            "coGrade": "일산화탄소 지수",
            "o3Grade": "오존 지수",
            "no2Grade": "이산화질소 지수",
            "pm10Grade": "미세먼지(PM10) 24시간 등급",
            "pm25Grade": "초미세먼지(PM2.5) 24시간 등급",
            "pm10Grade1h": "미세먼지(PM10) 1시간 등급",
            "pm25Grade1h": "초미세먼지(PM2.5) 1시간 등급",
            "so2Flag": "아황산가스 플래그",
            "coFlag": "일산화탄소 플래그",
            "o3Flag": "오존 플래그",
            "no2Flag": "이산화질소 플래그",
            "pm10Flag": "미세먼지(PM10) 플래그",
            "pm25Flag": "초미세먼지(PM2.5) 플래그"
        }
        return self._getDataFrameCommon('getMsrstnAcctoRltmMesureDnsty', params, parser_info, change_header_name)
    
    def getCityMeasurement(self, name: str, change_header_name: bool = True):
        """
        시도별 실시간 측정정보
        """
        params = {
            "sidoName": name,
            "ver": "1.3"
        }
        parser_info = {
            "stationName": "측정소명",
            "mangName": "측정망 정보",
            "sidoName": "시도명",
            "dataTime": "측정일시",
            "so2Value": "아황산가스 농도",
            "coValue": "일산화탄소 농도",
            "o3Value": "오존 농도",
            "no2Value": "이산화질소 농도",
            "pm10Value": "미세먼지(PM10) 농도",
            "pm10Value24": "미세먼지(PM10) 24시간 예측이동농도",
            "pm25Value": "초미세먼지(PM2.5) 농도",
            "pm25Value24": "초미세먼지(PM2.5) 24시간 예측이동농도",
            "khaiValue": "통합대기환경수치",
            "khaiGrade": "통합대기환경지수",
            "so2Grade": "아황산가스 지수",
            "coGrade": "일산화탄소 지수",
            "o3Grade": "오존 지수",
            "no2Grade": "이산화질소 지수",
            "pm10Grade": "미세먼지(PM10) 24시간 등급",
            "pm25Grade": "초미세먼지(PM2.5) 24시간 등급",
            "pm10Grade1h": "미세먼지(PM10) 1시간 등급",
            "pm25Grade1h": "초미세먼지(PM2.5) 1시간 등급",
            "so2Flag": "아황산가스 플래그",
            "coFlag": "일산화탄소 플래그",
            "o3Flag": "오존 플래그",
            "no2Flag": "이산화질소 플래그",
            "pm10Flag": "미세먼지(PM10) 플래그",
            "pm25Flag": "초미세먼지(PM2.5) 플래그"
        }
        return self._getDataFrameCommon('getCtprvnRltmMesureDnsty', params, parser_info, change_header_name)


if __name__ == "__main__":
    obj = AirQuality()
    df1 = obj.getAirQualityPrediction("2022-01-12")
    df2 = obj.getCurrentBadAirObservatoryInfo()
    df3 = obj.getWeeklyDustPredict("2022-01-11")
    df4 = obj.getObservatoryMeasurement("광교동", 1)
    df5 = obj.getCityMeasurement("서울")