import streamlit as st
from fashionRecommendation import FashionRecommendation

fr = FashionRecommendation()
fr.getData()

st.markdown("##### Fashion Information")
st.write(fr.fashion_list)

st.markdown("##### 최저가")
fr.getLowestPrices()
st.json(fr.lowest_prices)


st.markdown("##### Brand 정보")
brands = fr.fashion_list["브랜드"].to_list()
brand = st.selectbox("select brand", brands)
if brand != "":
    fr.getBrandPrice(brand)
    st.json(fr.brand_info)

st.markdown("##### Category Min / Max 정보")
categories = fr.fashion_list.columns.to_list()
categories.remove("브랜드")
category = st.selectbox("select category", categories)
if category != "":
    fr.getMinMaxPriceBrand(category)
    st.json(fr.category_min_max_price)


st.markdown("##### Insert / Update / Delete")

example_insert = """{"action" : "insert","data" : {"브랜드":"Y", "상의":1000, "아우터": 5000, "바지":4000, "스니커즈":9900, "가방":2200, "모자":1000, "양말":1000, "액세서리":2000}}"""

example_update = """{"action" : "update","data" : {"브랜드":"A", "모자":12000, "액세서리":2000}}"""
example_delete = """{"action" : "delete","data" : {"브랜드":"B"}}"""

st.markdown("###### Insert Example")
st.code(example_insert, language="json")
st.markdown("###### Update Example")
st.code(example_update, language="json")
st.markdown("###### Delete Example")
st.code(example_delete, language="json")

cmd = st.text_area("cmd")
if cmd != "":
    res, err = fr.upsertData(cmd)
    st.write(err)
    st.write(fr.fashion_list)
