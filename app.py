from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from werkzeug.utils import secure_filename
import os
import time   # để đo thời gian


# =============================================================
#  CẤU TRÚC NODE KHÁCH HÀNG
# =============================================================
class CustomerNode:
    def __init__(self, customer_id, name, phone):
        self.id = customer_id
        self.name = name
        self.phone = phone
        self.left = None
        self.right = None


# =============================================================
#  CÂY BST CÂN BẰNG THEO REBUILD
# =============================================================
class CustomerBST:
    def __init__(self):
        self.root = None
        self.auto_id = 1

    # ---------------------------------------------------------
    # THÊM KHÁCH HÀNG – ID TỰ TĂNG + REBUILD CÂY CÂN BẰNG
    # ---------------------------------------------------------
    def insert_auto(self, name, phone):
        customer_id = self.auto_id
        self.auto_id += 1

        new_node = CustomerNode(customer_id, name, phone)

        if self.root is None:
            self.root = new_node
        else:
            current = self.root
            while True:
                if customer_id < current.id:
                    if current.left is None:
                        current.left = new_node
                        break
                    current = current.left
                else:
                    if current.right is None:
                        current.right = new_node
                        break
                    current = current.right

        # Sau khi chèn xong → rebuild lại BST thành balanced BST
        self.rebuild_balanced()
        return customer_id

    # ---------------------------------------------------------
    # REBUILD LẠI BST THÀNH CÂY CÂN BẰNG
    # ---------------------------------------------------------
    def rebuild_balanced(self):
        nodes = self.to_list()  # inorder sorted
        arr = [(n.id, n.name, n.phone) for n in nodes]

        def build(start, end):
            if start > end:
                return None
            mid = (start + end) // 2
            cid, name, phone = arr[mid]
            node = CustomerNode(cid, name, phone)
            node.left = build(start, mid - 1)
            node.right = build(mid + 1, end)
            return node

        self.root = build(0, len(arr) - 1)

        if arr:
            self.auto_id = arr[-1][0] + 1
        else:
            self.auto_id = 1

    # ---------------------------------------------------------
    # TEXT MÔ TẢ VỊ TRÍ NODE (ROOT → LEFT/RIGHT ...)
    # ---------------------------------------------------------
    def _position_descriptor(self, path):
        if not path:
            return "Root (Level 0)"
        text = "Root"
        level = len(path)
        for p in path:
            text += " → Left" if p == "L" else " → Right"
        return f"{text} (Level {level})"

    # ---------------------------------------------------------
    # TÌM THEO ID – TRẢ VỀ NODE + VỊ TRÍ
    # ---------------------------------------------------------
    def search_by_id(self, customer_id):
        current = self.root
        path = []

        while current:
            if customer_id == current.id:
                return current, self._position_descriptor(path)
            elif customer_id < current.id:
                path.append("L")
                current = current.left
            else:
                path.append("R")
                current = current.right

        return None, None

    # ---------------------------------------------------------
    # TÌM THEO TÊN
    # ---------------------------------------------------------
    def search_by_name(self, name):
        result = []
        self._search_by_name_recursive(self.root, name.lower(), [], result)
        return result

    def _search_by_name_recursive(self, node, name, path, result):
        if node is None:
            return
        self._search_by_name_recursive(node.left, name, path + ["L"], result)
        if node.name.lower() == name:
            result.append((node, self._position_descriptor(path)))
        self._search_by_name_recursive(node.right, name, path + ["R"], result)

    # ---------------------------------------------------------
    # TÌM THEO SỐ ĐIỆN THOẠI
    # ---------------------------------------------------------
    def search_by_phone(self, phone):
        result = []
        self._search_by_phone_recursive(self.root, phone, [], result)
        return result

    def _search_by_phone_recursive(self, node, phone, path, result):
        if node is None:
            return
        self._search_by_phone_recursive(node.left, phone, path + ["L"], result)
        if node.phone == phone:
            result.append((node, self._position_descriptor(path)))
        self._search_by_phone_recursive(node.right, phone, path + ["R"], result)

    # ---------------------------------------------------------
    # XÓA THEO ID
    # ---------------------------------------------------------
    def delete(self, customer_id):
        self.root = self._delete_recursive(self.root, customer_id)

    def _delete_recursive(self, node, customer_id):
        if node is None:
            return node

        if customer_id < node.id:
            node.left = self._delete_recursive(node.left, customer_id)
        elif customer_id > node.id:
            node.right = self._delete_recursive(node.right, customer_id)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            min_node = self._min_value_node(node.right)
            node.id = min_node.id
            node.name = min_node.name
            node.phone = min_node.phone
            node.right = self._delete_recursive(node.right, min_node.id)

        return node

    def _min_value_node(self, node):
        while node.left:
            node = node.left
        return node

    # ---------------------------------------------------------
    # TRẢ VỀ DANH SÁCH NODE (INORDER)
    # ---------------------------------------------------------
    def to_list(self):
        result = []
        self._collect_inorder(self.root, result)
        return result

    def _collect_inorder(self, node, result):
        if node:
            self._collect_inorder(node.left, result)
            result.append(node)
            self._collect_inorder(node.right, result)

    # ---------------------------------------------------------
    # CHUYỂN CÂY SANG DICT ĐỂ VẼ TRÊN HTML
    # ---------------------------------------------------------
    def to_dict(self, node=None):
        # Cho phép gọi to_dict() không tham số
        if node is None:
            node = self.root
        if node is None:
            return None

        return {
            "id": node.id,
            "name": node.name,
            "phone": node.phone,
            "left": self.to_dict(node.left) if node.left else None,
            "right": self.to_dict(node.right) if node.right else None
        }

    # ---------------------------------------------------------
    # TÌM THEO ID + TRẢ VỀ CHUỖI CÁC BƯỚC (CHO MÔ PHỎNG)
    # ---------------------------------------------------------
    def search_by_id_with_steps(self, customer_id):
        current = self.root
        steps = []

        while current:
            if customer_id == current.id:
                steps.append(f"FOUND → {current.id}")
                return current, steps
            elif customer_id < current.id:
                steps.append(f"{current.id} → Left")
                current = current.left
            else:
                steps.append(f"{current.id} → Right")
                current = current.right

        steps.append("NOT FOUND")
        return None, steps


# =============================================================
#  CÂY AVL (xoay trái / phải)
# =============================================================
class CustomerAVL:
    def __init__(self):
        self.root = None
        self.auto_id = 1

    class Node:
        def __init__(self, cid, name, phone):
            self.id = cid
            self.name = name
            self.phone = phone
            self.left = None
            self.right = None
            self.height = 1

    # ===== Height & Balance =====
    def _h(self, n):
        return n.height if n else 0

    def _bf(self, n):
        if not n:
            return 0
        return self._h(n.left) - self._h(n.right)

    # ===== Rotations =====
    def _right(self, y):
        x = y.left
        t = x.right
        x.right = y
        y.left = t
        y.height = 1 + max(self._h(y.left), self._h(y.right))
        x.height = 1 + max(self._h(x.left), self._h(x.right))
        return x

    def _left(self, x):
        y = x.right
        t = y.left
        y.left = x
        x.right = t
        x.height = 1 + max(self._h(x.left), self._h(x.right))
        y.height = 1 + max(self._h(y.left), self._h(y.right))
        return y

    # ===== Insert =====
    def insert_auto(self, name, phone):
        cid = self.auto_id
        self.auto_id += 1
        self.root = self._insert(self.root, cid, name, phone)
        return cid

    def _insert(self, n, cid, name, phone):
        if not n:
            return self.Node(cid, name, phone)

        if cid < n.id:
            n.left = self._insert(n.left, cid, name, phone)
        else:
            n.right = self._insert(n.right, cid, name, phone)

        n.height = 1 + max(self._h(n.left), self._h(n.right))
        bf = self._bf(n)

        # LL
        if bf > 1 and cid < n.left.id:
            return self._right(n)

        # RR
        if bf < -1 and cid > n.right.id:
            return self._left(n)

        # LR
        if bf > 1 and cid > n.left.id:
            n.left = self._left(n.left)
            return self._right(n)

        # RL
        if bf < -1 and cid < n.right.id:
            n.right = self._right(n.right)
            return self._left(n)

        return n

    # ===== Delete =====
    def delete(self, cid):
        self.root = self._delete(self.root, cid)

    def _min(self, n):
        while n.left:
            n = n.left
        return n

    def _delete(self, n, cid):
        if not n:
            return n

        if cid < n.id:
            n.left = self._delete(n.left, cid)
        elif cid > n.id:
            n.right = self._delete(n.right, cid)
        else:
            if not n.left:
                return n.right
            if not n.right:
                return n.left

            t = self._min(n.right)
            n.id, n.name, n.phone = t.id, t.name, t.phone
            n.right = self._delete(n.right, t.id)

        if not n:
            return n

        n.height = 1 + max(self._h(n.left), self._h(n.right))
        bf = self._bf(n)

        if bf > 1 and self._bf(n.left) >= 0:
            return self._right(n)
        if bf > 1 and self._bf(n.left) < 0:
            n.left = self._left(n.left)
            return self._right(n)
        if bf < -1 and self._bf(n.right) <= 0:
            return self._left(n)
        if bf < -1 and self._bf(n.right) > 0:
            n.right = self._right(n.right)
            return self._left(n)

        return n

    # ===== Inorder =====
    def to_list(self):
        res = []
        self._in(n=self.root, out=res)
        return res

    def _in(self, n, out):
        if n:
            self._in(n.left, out)
            out.append(n)
            self._in(n.right, out)

    # ===== Convert to dict for HTML =====
    def to_dict(self, node=None):
        if node is None:
            node = self.root
        if node is None:
            return None

        return {
            "id": node.id,
            "name": node.name,
            "phone": node.phone,
            "left": self.to_dict(node.left) if node.left else None,
            "right": self.to_dict(node.right) if node.right else None
        }

    # ===== TEXT VỊ TRÍ + SEARCH ĐỂ SO SÁNH THỜI GIAN =====
    def _position_descriptor(self, path):
        if not path:
            return "Root (Level 0)"
        text = "Root"
        level = len(path)
        for p in path:
            text += " → Left" if p == "L" else " → Right"
        return f"{text} (Level {level})"

    def search_by_id(self, customer_id):
        current = self.root
        path = []

        while current:
            if customer_id == current.id:
                return current, self._position_descriptor(path)
            elif customer_id < current.id:
                path.append("L")
                current = current.left
            else:
                path.append("R")
                current = current.right

        return None, None

    def search_by_id_with_steps(self, customer_id):
        current = self.root
        steps = []

        while current:
            if customer_id == current.id:
                steps.append(f"FOUND → {current.id}")
                return current, steps
            elif customer_id < current.id:
                steps.append(f"{current.id} → Left")
                current = current.left
            else:
                steps.append(f"{current.id} → Right")
                current = current.right

        steps.append("NOT FOUND")
        return None, steps

    def search_by_name(self, name):
        result = []
        self._search_by_name_recursive(self.root, name.lower(), [], result)
        return result

    def _search_by_name_recursive(self, node, name, path, result):
        if node is None:
            return
        self._search_by_name_recursive(node.left, name, path + ["L"], result)
        if node.name.lower() == name:
            result.append((node, self._position_descriptor(path)))
        self._search_by_name_recursive(node.right, name, path + ["R"], result)

    def search_by_phone(self, phone):
        result = []
        self._search_by_phone_recursive(self.root, phone, [], result)
        return result

    def _search_by_phone_recursive(self, node, phone, path, result):
        if node is None:
            return
        self._search_by_phone_recursive(node.left, phone, path + ["L"], result)
        if node.phone == phone:
            result.append((node, self._position_descriptor(path)))
        self._search_by_phone_recursive(node.right, phone, path + ["R"], result)


# =============================================================
# FLASK APP
# =============================================================
app = Flask(__name__)
app.secret_key = "super-secret-key"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

customer_bst = CustomerBST()          # Balanced BST (rebuild)
customer_bst_plain = CustomerAVL()    # AVL rotation


# =============================================================
# Seed Data
# =============================================================
def seed_data():
    data = [
        ("Nguyen Van A", "0901234567"),
        ("Tran Thi B", "0988333444"),
        ("Le Van C", "0911222333"),
        ("Pham Thi D", "0933444555"),
        ("Nguyen Van A", "0999888777"),
        ("Pham Thi F", "0977665544"),
    ]

    for name, phone in data:
        customer_bst.insert_auto(name, phone)
        customer_bst_plain.insert_auto(name, phone)


seed_data()


# =============================================================
# ROUTES
# =============================================================
@app.route("/")
def index():
    customers = customer_bst.to_list()
    return render_template(
        "index.html",
        customers=customers,
        search_results=None,
        search_query="",
        search_type="id",
    )


# -------------------------------------------------------------
# Thêm khách hàng + đo thời gian insert cho 2 cây
# -------------------------------------------------------------
@app.route("/add", methods=["POST"])
def add_customer():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not phone:
        flash("Tên và số điện thoại không được để trống!", "error")
        return redirect(url_for("index"))

    # BST
    start_bst = time.time()
    new_id = customer_bst.insert_auto(name, phone)
    end_bst = time.time()

    # AVL
    start_avl = time.time()
    customer_bst_plain.insert_auto(name, phone)
    end_avl = time.time()

    bst_time = (end_bst - start_bst) * 1000
    avl_time = (end_avl - start_avl) * 1000

    flash(f"Thêm khách hàng ID {new_id} thành công!", "success")
    flash(f"⏱ Insert BST (rebuild): {bst_time:.3f} ms", "info")
    flash(f"⏱ Insert AVL (rotation): {avl_time:.3f} ms", "info")

    return redirect(url_for("index"))


# -------------------------------------------------------------
# Xóa khách hàng + đo thời gian delete cho 2 cây
# -------------------------------------------------------------
@app.route("/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    node, _ = customer_bst.search_by_id(customer_id)
    if not node:
        flash("Không tìm thấy khách hàng để xóa!", "error")
        return redirect(url_for("index"))

    # BST
    start_bst = time.time()
    customer_bst.delete(customer_id)
    end_bst = time.time()

    # AVL
    start_avl = time.time()
    customer_bst_plain.delete(customer_id)
    end_avl = time.time()

    bst_time = (end_bst - start_bst) * 1000
    avl_time = (end_avl - start_avl) * 1000

    flash(f"Đã xóa khách hàng có ID {customer_id}", "success")
    flash(f"⏱ Delete BST (rebuild): {bst_time:.3f} ms", "info")
    flash(f"⏱ Delete AVL (rotation): {avl_time:.3f} ms", "info")

    return redirect(url_for("index"))


# -------------------------------------------------------------
# Tìm kiếm khách hàng + so sánh thời gian search 2 cây
# -------------------------------------------------------------
@app.route("/search", methods=["POST"])
def search_customer():
    search_type = request.form.get("search_type")
    query = request.form.get("query", "").strip()

    customers = customer_bst.to_list()
    results = []

    if not query:
        flash("Vui lòng nhập nội dung cần tìm!", "error")
        return render_template(
            "index.html",
            customers=customers,
            search_results=None,
            search_query="",
            search_type=search_type,
        )

    bst_time = avl_time = None

    if search_type == "id":
        try:
            cid = int(query)
        except ValueError:
            flash("ID phải là số!", "error")
            return redirect(url_for("index"))

        # BST search
        start_bst = time.time()
        node, pos = customer_bst.search_by_id(cid)
        end_bst = time.time()

        # AVL search
        start_avl = time.time()
        node_avl, pos_avl = customer_bst_plain.search_by_id(cid)
        end_avl = time.time()
        bst_time = (end_bst - start_bst) * 1000000
        avl_time = (end_avl - start_avl) * 1000000

        if node:
            results.append({"node": node, "position": pos})

    elif search_type == "name":
        # BST
        start_bst = time.time()
        bst_res = customer_bst.search_by_name(query)
        end_bst = time.time()

        # AVL
        start_avl = time.time()
        avl_res = customer_bst_plain.search_by_name(query)
        end_avl = time.time()

        bst_time = (end_bst - start_bst) * 1000000
        avl_time = (end_avl - start_avl) * 1000000

        for node, pos in bst_res:
            results.append({"node": node, "position": pos})

    elif search_type == "phone":
        # BST
        start_bst = time.time()
        bst_res = customer_bst.search_by_phone(query)
        end_bst = time.time()

        # AVL
        start_avl = time.time()
        avl_res = customer_bst_plain.search_by_phone(query)
        end_avl = time.time()

        bst_time = (end_bst - start_bst) * 1000000
        avl_time = (end_avl - start_avl) * 1000000

        for node, pos in bst_res:
            results.append({"node": node, "position": pos})

    if not results:
        flash("Không tìm thấy khách hàng phù hợp!", "error")

    if bst_time is not None and avl_time is not None:
        flash(f"⏱ Search BST (rebuild): {bst_time:.6f} ns", "info")
        flash(f"⏱ Search AVL (rotation): {avl_time:.6f} ns", "info")

    return render_template(
        "index.html",
        customers=customers,
        search_results=results,
        search_query=query,
        search_type=search_type,
    )


# -------------------------------------------------------------
# TREE BST – dùng để mô phỏng riêng BST
# -------------------------------------------------------------
@app.route("/tree")
def show_tree():
    tree = customer_bst.to_dict()
    return render_template("tree.html", tree=tree, steps=None)


@app.route("/tree_search", methods=["POST"])
def tree_search():
    try:
        cid = int(request.form.get("search_id"))
    except (TypeError, ValueError):
        cid = None

    tree = customer_bst.to_dict()

    if cid is None:
        return render_template("tree.html", tree=tree, steps=["ID không hợp lệ!"])

    node, steps = customer_bst.search_by_id_with_steps(cid)
    return render_template("tree.html", tree=tree, steps=steps)


# -------------------------------------------------------------
# UPLOAD – chèn cho cả 2 cây + đo thời gian
# -------------------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    if filename.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    elif filename.endswith(".csv"):
        df = pd.read_csv(filepath)
    else:
        flash("Chỉ hỗ trợ file .xlsx hoặc .csv!", "error")
        return redirect(url_for("index"))

    required = {"name", "phone"}
    if not required.issubset(df.columns):
        flash("File phải có 2 cột: name, phone", "error")
        return redirect(url_for("index"))

    # BST
    start_bst = time.time()
    count = 0
    for _, row in df.iterrows():
        name = str(row["name"])
        phone = str(row["phone"])
        customer_bst.insert_auto(name, phone)
        count += 1
    end_bst = time.time()
    bst_time = (end_bst - start_bst) * 1000

    # AVL
    start_avl = time.time()
    for _, row in df.iterrows():
        name = str(row["name"])
        phone = str(row["phone"])
        customer_bst_plain.insert_auto(name, phone)
    end_avl = time.time()
    avl_time = (end_avl - start_avl) * 1000

    flash(f"Đã thêm {count} khách hàng từ file.", "success")
    flash(f"⏱ Upload + insert BST (rebuild): {bst_time:.3f} ms", "info")
    flash(f"⏱ Upload + insert AVL (rotation): {avl_time:.3f} ms", "info")

    return redirect(url_for("index"))


# -------------------------------------------------------------
# AVL PAGE – SO SÁNH CẤU TRÚC + MÔ PHỎNG TÌM KIẾM CẢ 2 CÂY
# -------------------------------------------------------------
@app.route("/avl")
def compare_trees():
    search_id = request.args.get("search_id", type=int)

    avl_tree = customer_bst.to_dict()            # BST (balanced rebuild)
    bst_tree = customer_bst_plain.to_dict()      # AVL (rotation)

    bst_steps = []
    avl_steps = []

    if search_id is not None:
        _, bst_steps = customer_bst.search_by_id_with_steps(search_id)
        _, avl_steps = customer_bst_plain.search_by_id_with_steps(search_id)

    return render_template(
        "avl.html",
        avl_tree=avl_tree,
        bst_tree=bst_tree,
        bst_steps=bst_steps,
        avl_steps=avl_steps
    )


# =============================================================
# RUN APP
# =============================================================
if __name__ == "__main__":
    print("BST root:", customer_bst.root)
    print("AVL root:", customer_bst_plain.root)
    app.run(debug=True)
