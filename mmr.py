# 导入NumPy库
import numpy as np


# 定义余弦相似度计算函数
def cosine_similarity(from_vec, to_vecs):
    """
    计算一个向量与多个向量的余弦相似度

    参数:
        from_vec: 单个向量（1D或2D数组或列表）
        to_vecs: 多个向量（2D或3D数组，每一行为一个向量）

    返回:
        一维数组，包含单个向量与每个多个向量的相似度

    示例:
        sims = cosine_similarity(from_vec, to_vecs)
    """
    # 将from_vec转换为NumPy数组并强制类型为float
    from_vec = np.array(from_vec, dtype=float)
    # 将to_vecs转换为NumPy数组并强制类型为float
    to_vecs = np.array(to_vecs, dtype=float)

    # 计算from_vec的范数（模长）
    norm1 = np.linalg.norm(from_vec)
    # 如果from_vec是零向量，直接返回全0相似度数组
    if norm1 == 0:
        return np.zeros(len(to_vecs))

    # 初始化用于存储相似度的列表
    similarities = []
    # 遍历每一个待比较的向量to_vec
    for to_vec in to_vecs:
        # 计算from_vec和to_vec的点积
        dot_product = np.sum(from_vec * to_vec)
        # 计算to_vec的模长（范数）
        norm_vec = np.linalg.norm(to_vec)
        # 如果to_vec为零向量，相似度设为0
        if norm_vec == 0:
            similarities.append(0.0)
        else:
            # 计算余弦相似度
            similarity = dot_product / (norm1 * norm_vec)
            similarities.append(similarity)

    # 将列表转换为NumPy数组后返回
    return np.array(similarities)


# 封装MMR算法为函数
def mmr_select(query_vector, doc_vectors, k=3, lambda_mult=0.5):
    """
    使用最大边际相关性（MMR）算法选择文档

    参数:
        query_vector: 查询向量（1D数组）
        doc_vectors: 文档向量集合（2D数组，每行一个文档向量）
        k: 要选择的文档数量（默认3）
        lambda_mult: λ参数，平衡相关性与多样性（默认0.5）
                     - λ=1: 只看相关性
                     - λ=0: 只看多样性
                     - λ=0.5: 平衡相关性和多样性

    返回:
        selected: 选中的文档索引列表（从0开始）

    示例:
        selected = mmr_select(query_vector, doc_vectors, k=3, lambda_mult=0.5)
    """
    # 计算所有文档与查询向量的余弦相似度
    query_similarities = cosine_similarity(query_vector, doc_vectors)

    # 打印所有文档与查询向量的余弦相似度分数
    print("文档与查询的相关性分数：")
    for i, sim in enumerate(query_similarities):
        # 依次输出文档编号（从1开始）及其相似度分数
        print(f"文档{i+1}: {sim:.4f}")

    # 找到与查询最相关的文档的下标，作为初始已选文档
    selected = [int(np.argmax(query_similarities))]

    # 不断循环直到已选择k个文档
    while len(selected) < k:
        # 存储每个未选文档的MMR分数（二元组）
        mmr_scores = []
        # 遍历所有文档编号
        for i in range(len(doc_vectors)):
            # 如果当前文档未被选择
            if i not in selected:
                # 获取当前文档与查询的相关性分数
                relevance = query_similarities[i]
                # 获取当前已选文档的向量集合
                selected_vecs = doc_vectors[selected]
                # 计算当前文档与所有已选文档的余弦相似度
                sims = cosine_similarity(doc_vectors[i], selected_vecs)
                # 取对已选集中最大相似度（最“不多样性的”）
                max_sim = np.max(sims)
                # 按MMR公式计算分数
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_sim
                # 存储该文档的编号和分数
                mmr_scores.append((i, mmr_score))

        # 如果没有可选文档则跳出循环
        if not mmr_scores:
            break

        # 选取MMR分数最高的文档编号
        best_idx, best_score = max(mmr_scores, key=lambda x: x[1])
        # 将选中的文档添加到已选列表
        selected.append(best_idx)

    # 返回最终已选文档的索引
    return selected


# 使用示例区域
# 设置λ参数，权衡相关性与多样性
lambda_mult = 0.5
# 指定需要选择的文档数量k
k = 3
# 构造查询向量（比如“人工智能”主题）
query_vector = np.array([4, 2])

# 构造待选文档的向量列表
doc_vectors = np.array([[9, 2], [2, 9], [7, 8], [1, 3], [6, 1]])
# 调用MMR算法选择文档
selected = mmr_select(query_vector, doc_vectors, k=k, lambda_mult=lambda_mult)

# 打印最终选中的所有文档的编号（转换为从1计算的序号）
print(f"\nλ={lambda_mult:.1f}: 最终选择文档 {[int(s)+1 for s in selected]}")
