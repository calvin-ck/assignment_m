import pandas as pd
import random
import json
from IPython.display import HTML

class FashionRecommendation:
    def __init__(self):
        self.data_file = "fashion_list.csv"

    # fashion data 를 가져온다.
    def getData(self):
        self.fashion_list = pd.read_csv(self.data_file)

    # fashion_list 출력용.
    def printData(self):
        self.print_fashion_list = self.fashion_list.copy()
        for column in self.print_fashion_list.columns:
            if column != "브랜드":
                self.print_fashion_list[column] = self.print_fashion_list[column].apply(lambda x: format(x, ','))
        # print (self.print_fashion_list.to_markdown(index=False))
        # HTML (self.print_fashion_list.to_html(index=False))

    # 최소값에 해당하는 brand 정보 가져오기.
    def getBrandInfoByPrice(self, category, price, return_all, rand_yn):
        # 해당 카테고리 별 최소값의 랜드를 가져온다.
        brand_list = self.fashion_list[self.fashion_list[category] == price]["브랜드"].to_list()
        # 전체 목록 반환 
        if return_all :
            return brand_list

        # 하나만 반환해야 한다면
        brand = brand_list[0]
        if rand_yn == True and len(brand_list) > 1:
            #랜덤으로.
            idx = random.randrange(len(brand_list))
            brand = brand_list[idx]
        return brand
    
    ### 구현 1) - 카테고리 별 최저가격 브랜드와 상품 가격, 총액을 조회하는 API
    def getLowestPrices(self):
        # 각 카테고리별 최소값을 가져온다.
        min_infos = self.fashion_list.min().to_dict()

        # json 생성.
        total_price = 0
        category_infos = []
        for category, price in min_infos.items():
            # category 가 '브랜드' 인 정보는 필요 없다.
            if category == "브랜드":
                continue

            total_price += price
            
            # 우선 설정은 중복된 최저가격이 있으면, 랜덤으로 하나만 가져 오는 것으로.
            brand = self.getBrandInfoByPrice(category, price, False, True)
            category_info = {
                "카테고리" : category,
                "브랜드" : brand,
                "가격" : format(price, ",")
            }
            category_infos.append(category_info)
            
        self.lowest_prices_dict = {
            "category_infos" : category_infos,
            "총액" : format(total_price, ",")
        }
        self.lowest_prices = json.dumps( self.lowest_prices_dict, ensure_ascii=False)

    ### 구현 2) - 단일 브랜드로 모든 카테고리 상품을 구매할 때 최저가격에 판매하는 브랜드와 카테고리의 상품가격
    ###, 총액을 조회하는 API
    def getBrandPrice(self, brand):
        brands = self.fashion_list["브랜드"].to_list()
        if brand not in brands:
            return False, "입력한 브랜드는 목록에 없습니다."
    
        price_info = self.fashion_list[self.fashion_list["브랜드"] == brand].to_dict('records')[0]
        category_info= []
        total_price = 0
        for category, price in price_info.items():
            if category == "브랜드":
                continue
            category_info.append({"카테고리": category,
                                 "가격":format(price, ",")})
            total_price += price
        
        self.brand_info_dict = {
            "최저가" : {
                "브랜드" : brand,
                "카테고리" : category_info,
                "총액" : format(total_price, ",")
            }
        }
        self.brand_info = json.dumps( self.brand_info_dict, ensure_ascii=False)
        return True, ""

    ### 구현 3) - 카테고리 이름으로 최저, 최고 가격 브랜드와 상품 가격을 조회하는 API
    def getMinMaxPriceBrand(self, category):
        categories = self.fashion_list.columns.to_list()
        categories.remove("브랜드")
        # input category 가 없을 때.
        if category not in categories:
            return False, "입력한 카테고리 정보가 없습니다."
            
        prices = self.fashion_list[category]
        min_price = prices.min().item()
        max_price = prices.max().item()
        min_brand = self.getBrandInfoByPrice(category, min_price, True, False)
        max_brand = self.getBrandInfoByPrice(category, max_price, True, False)

        min_info = [{"브랜드":brand, "가격":format(min_price, ",")} for brand in min_brand]
        max_info = [{"브랜드":brand, "가격":format(max_price, ",")} for brand in max_brand]

        self.category_min_max_price_dict = {
            "카테고리" : category,
            "최저가" : min_info,
            "최고가" : max_info
        }
        self.category_min_max_price = json.dumps( self.category_min_max_price_dict, ensure_ascii=False)

        return True, ""

    ### 구현 4) 브랜드 및 상품을 추가 / 업데이트 / 삭제하는 API
    def upsertData(self, json_str):
        json_str = json_str.strip()
        # action & data 추출
        if len(json_str) == 0:
            return False, "올바른 입력을 넣으세요."
        try :
            d = json.loads(json_str)
        except Exception as e:
            return False, "올바른 json 형식을 입력해 주세요. (%s)" % e
        if "action" not in d or "data" not in d:
            return False, "json 에는 'action'과 'data'가 있어야 합니다."
            
        action = d["action"]
        data = d["data"]

        if type(data) is not dict:
            return False, "data는 dictionary type 이어야 합니다."

        # data 적합성 확인
        if action not in ["insert", "delete", "update"]:
            return False, "action 은 insert, delete, update 중 하나여야 합니다."
            
        # 현재 dataset 에서 브랜드와 카테고리 정보를 가져온다.
        brands = self.fashion_list["브랜드"].to_list()
        categories = self.fashion_list.columns.to_list()
        categories.remove("브랜드")

        if "브랜드" not in data.keys():
            return False, "data 에 '브랜드'는 필수입니다."
        for category in data.keys():
            if category == "브랜드":
                continue
            if category not in categories:
                return False, "%s는 카테고리에 없습니다." % category

        # 입력된 정보에서....
        brand = data["브랜드"]

        if action == "insert":
            if brand in brands:
                return False, "브랜드 %s 는 이미 존재합니다." % brand
            try :
                self.fashion_list = pd.concat([self.fashion_list, pd.DataFrame.from_dict([data])], ignore_index=True)
            except Exception as e:
                return False, "데이터 입력에 실패하였습니다. (%s)" % e
        elif action == "delete":
            if brand not in brands:
                return False, "브랜드 %s 는 존재하지 않습니다." % brand
            self.fashion_list = self.fashion_list[self.fashion_list["브랜드"] != brand]
        elif action == "update":
            if brand not in brands:
                return False, "브랜드 %s 는 존재하지 않습니다." % brand
            for c, v in data.items():
                if c != "브랜드":
                    self.fashion_list.loc[self.fashion_list.브랜드 == brand, c] = v
            
        return True, ""
