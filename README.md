# Example_data

课程示例数据。文件的来源、年份和许可应按各数据项分别核对。

## 2020 年县级常住人口

`china_county_population_2020.csv` 从 [Lei Dong 团队的第七次人口普查年鉴整理表](https://github.com/leiii/census)提取县级及四个不设区地级市的区划代码、名称和常住人口，共 2,947 条。`china_sansha_population_2020.csv` 从同一工作表提取三沙市总数及西沙、南沙、中沙三个分项，共 4 条；原表中三个分项没有六位县级代码，因此单独保存，用于课堂地图脚本核对。原项目采用 MIT License；许可文本见 [`licenses/leiii-census-MIT.txt`](licenses/leiii-census-MIT.txt)。

两个 CSV 均为 **2020 年人口数据**，不包含行政区边界。运行第四章的县级地图示例时，把两个文件放在章节的 `data/` 目录；另外需要按来源授权取得 `中国_县`、`中国_市`、`中国_省`、`国界线`、`十段线` 五组边界文件，并通过 `CHINA_DIVISION_DIR` 指向其所在文件夹。与其他年份边界连接时，应同时检查区划代码和名称，并将无法稳妥匹配的单元标为缺失。

## 中国行政区边界来源说明

现有 `shanghai_boundary.geojson` 的原始来源和审图号对应文件尚待核验。此前 README 中的 `GS（2024）0650号` 不能据此认作该 GeoJSON 或由其重绘专题图的审图号。用户提供的全国省、市、县 SHP 已在本地转换和试绘，但未确认公开再分发许可，因此暂未加入本仓库。
