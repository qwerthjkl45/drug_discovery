import sqlite3

# 连接到数据库文件
conn = sqlite3.connect('/chembl_33/chembl_33.db')

# 创建游标对象
cursor = conn.cursor()

try:
    # 执行查询
    cursor.execute("""
        
SELECT
    molecule_dictionary.chembl_id,
    activities.activity_id,
    activities.standard_value,
    activities.standard_units,
    assays.assay_type,
    target_dictionary.tid,
    target_dictionary.pref_name,
    domains.domain_name
FROM
    activities
JOIN
    molecule_dictionary ON activities.molregno = molecule_dictionary.molregno
JOIN
    assays ON activities.assay_id = assays.assay_id	
JOIN
    target_dictionary ON assays.tid = target_dictionary.tid
JOIN
    target_components ON target_components.tid = target_dictionary.tid
JOIN	
    component_sequences ON target_components.component_id = component_sequences.component_id
JOIN
    component_domains ON component_sequences.component_id = component_domains.component_id
JOIN
    domains ON domains.domain_id = component_domains.domain_id	
WHERE
    molecule_dictionary.chembl_id = 'CHEMBL3895648'
    AND activities.standard_type = 'IC50';
    """)

    # 获取查询结果
    result = cursor.fetchall()

    # 打印结果
    for row in result:
        print(row)

finally:
    # 关闭连接
    conn.close()
