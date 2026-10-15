# Example_data

课程示例数据。文件的来源、年份和许可应按各数据项分别核对。

## 2020 年县级常住人口

`china_county_population_2020.csv` 从 [Lei Dong 团队的第七次人口普查年鉴整理表](https://github.com/leiii/census)提取县级及四个不设区地级市的区划代码、名称和常住人口，共 2,947 条。`china_sansha_population_2020.csv` 从同一工作表提取三沙市总数及西沙、南沙、中沙三个分项，共 4 条；原表中三个分项没有六位县级代码，因此单独保存，用于课堂地图脚本核对。原项目采用 MIT License；许可文本见 [`licenses/leiii-census-MIT.txt`](licenses/leiii-census-MIT.txt)。

两个 CSV 均为 **2020 年人口数据**，不包含行政区边界。运行第四章的县级地图示例时，把两个文件放在章节的 `data/` 目录；另外需要按来源授权取得 `中国_县`、`中国_市`、`中国_省`、`国界线`、`十段线` 五组边界文件，并通过 `CHINA_DIVISION_DIR` 指向其所在文件夹。与其他年份边界连接时，应同时检查区划代码和名称，并将无法稳妥匹配的单元标为缺失。

## 中国行政区边界来源说明

现有 `shanghai_boundary.geojson` 的原始来源和审图号对应文件尚待核验。此前 README 中的 `GS（2024）0650号` 不能据此认作该 GeoJSON 或由其重绘专题图的审图号。用户提供的全国省、市、县 SHP 已在本地转换和试绘，但未确认公开再分发许可，因此暂未加入本仓库。

## 伦敦绿色基础设施框架（LGIF）

`london_lgif_hex350_scores_2026.geojson` 是 [Greater London Authority 的 London Green Infrastructure Framework](https://data.london.gov.uk/dataset/london-green-infrastructure-framework-lgif-e70pq) 教学用精简版。采用官方 **01.04.26 修正版**结果表，与 `Hex350_grid_GLA` 按 `hex_id` 一对一连接，保留全部 15,041 个 350 m 六角网格、`overall_need_txt`（综合需求）、`overall_provision_txt`（综合供给），以及十项目标各自的需求与供给分类字段（`so1_*` 至 `so10_*`）。这些字段均为官方低／中／高分类结果，并非连续测量值。源网格为 British National Grid（EPSG:27700）；GeoJSON 转为 WGS 84（EPSG:4326），没有简化几何。源表与网格的 ID 均唯一、无缺失且完全匹配；22 个分类字段无缺失；导出后重新读取，几何无空值或无效多边形。

`london_boroughs_os_2018.geojson` 是 [London Datastore 的伦敦行政区数据](https://data.london.gov.uk/dataset/london-boroughs-e55pw) 精简版，保留 33 个行政区的 `name` 与 `gss_code`。来源页标注为 **2018 年 Ordnance Survey Boundary-Line 提取数据**，并非 2026 年最新行政边界；GeoJSON 同样转为 EPSG:4326，未简化几何。

两个来源页均标注 **Open Government Licence v3.0**。资料署名：*Contains public sector information licensed under the Open Government Licence v3.0. Source: Greater London Authority, London Green Infrastructure Framework (2026).* 行政区边界还须保留 [Ordnance Survey 的 OS OpenData 署名](https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-licensing/copyright-acknowledgments)：*Contains OS data © Crown copyright and database right 2018.* 原始数据、字段字典、方法报告和配色说明见上方官方数据页。第四章本地的 `data/london_lgif_2026/prepare_lgif_geojson.R` 保存了重建与核查步骤。

## 上海微博空间分析课堂样本（2020—2025 年）

`weibo_sample_4pct.csv` 于 **2026 年 10 月 16 日**更新。数据提供者交付的源文件含 5,399,200 条记录，覆盖 2020 年 1 月至 2025 年 12 月的全部 72 个月。使用固定种子 `20261016`，对全部记录进行无放回简单随机抽样，精确抽取 **215,968 条（4%）**；抽样前不按年份、地区或坐标筛选，也不去重。研究时再按时间窗口和区界筛选。该比例针对源文件记录，不代表用户或人口的 4%，年份覆盖也不等于已经核实上海微博的完整采集覆盖。

新版只保留 `匿名用户ID`、`发布时间`、`经度`、`纬度`、`年份`、`月份`。坐标为数据提供者确认的 **WGS84**。匿名用户代码按样本内首次出现顺序生成，同一用户代码一致，不导出原 ID 或映射表；不保留微博正文、性别或地点类型。精确时空位置仍需谨慎使用。源文件和样本均未发现无效时间、年月不一致或基础坐标错误；真正的行政区归属仍需与边界进行空间匹配。各年数据规模不同，跨年变化还需结合采集条件和平台使用差异解释。

详细字段、年度数量及限制见 [`weibo_sample_4pct_README.md`](weibo_sample_4pct_README.md)，文件指纹和逐月质量检查见 [`weibo_sample_4pct_manifest.json`](weibo_sample_4pct_manifest.json)。重建脚本见 [`scripts/prepare_weibo_sample.py`](scripts/prepare_weibo_sample.py)，需由数据提供者另行提供原文件。课程不从文件名推定第三方采集来源、完整性保证或公开许可；使用与再分发范围由数据提供者核对。

## 第五章六区案例使用的边界（2026-10-16）

`shanghai_boundary_2025.geojson` 含上海16区，供黄浦、徐汇、长宁、静安、杨浦、闵行六区微博案例选取研究范围。坐标为WGS84；字段 `district_name` 为区名，`district_code` 为六位行政区代码。来源为课程提供者的本地2025年行政区划数据包，提取过程与来源范围见 `shanghai_boundary_2025_PROVENANCE.md`。未将数据包目录名中的审图号视为该文件或后续专题图的审图证明，未另行声称公开许可。旧 `shanghai_boundary.geojson` 保留，供原练习使用。
