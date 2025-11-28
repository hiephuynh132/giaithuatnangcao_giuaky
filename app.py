from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from werkzeug.utils import secure_filename
import os


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
#  CÂY BST QUẢN LÝ KHÁCH HÀNG
# =============================================================
class CustomerBST:
    def __init__(self):
        self.root = None
        self.auto_id = 1     # ID tự tăng bắt đầu từ 1


    # ---------------------------------------------------------
    # 1. THÊM KHÁCH HÀNG – ID TỰ SINH
    # ---------------------------------------------------------
    def insert_auto(self, name, phone):
        customer_id = self.auto_id
        self.auto_id += 1

        # Chèn tạm vào cây theo ID
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

        # 🔥 Sau khi chèn xong → cân bằng lại cây
        self.rebuild_balanced()
        return customer_id
    # ---------------------------------------------------------
    # CÂN BẰNG LẠI CÂY (BALANCED BST THEO ID)
    # ---------------------------------------------------------
    def rebuild_balanced(self):
        """Lấy tất cả node, sắp xếp theo ID, rồi build lại cây cân bằng."""
        nodes = self.to_list()  # to_list() là in-order → đã sorted theo id
        arr = [(n.id, n.name, n.phone) for n in nodes]

        def build_balanced(start, end):
            if start > end:
                return None
            mid = (start + end) // 2
            cid, name, phone = arr[mid]
            node = CustomerNode(cid, name, phone)
            node.left = build_balanced(start, mid - 1)
            node.right = build_balanced(mid + 1, end)
            return node

        self.root = build_balanced(0, len(arr) - 1)

        # Cập nhật lại auto_id = max_id + 1
        if arr:
            max_id = arr[-1][0]
            self.auto_id = max_id + 1
        else:
            self.auto_id = 1
    # ---------------------------------------------------------
    # HÀM TẠO MÔ TẢ VỊ TRÍ NODE
    # ---------------------------------------------------------
    def _position_descriptor(self, path):
        if not path:
            return "Root (Level 0)"

        text = "Root"
        level = len(path)

        for p in path:
            if p == 'L':
                text += " → Left"
            else:
                text += " → Right"

        return f"{text}  (Level {level})"

    # ---------------------------------------------------------
    # 2. TÌM THEO ID (O log n) + vị trí
    # ---------------------------------------------------------
    def search_by_id(self, customer_id):
        current = self.root
        path = []

        while current:
            if customer_id == current.id:
                return current, self._position_descriptor(path)

            elif customer_id < current.id:
                path.append('L')
                current = current.left

            else:
                path.append('R')
                current = current.right

        return None, None

    # ---------------------------------------------------------
    # 3. TÌM THEO TÊN (O n) + vị trí
    # ---------------------------------------------------------
    def search_by_name(self, name):
        result = []
        self._search_by_name_recursive(self.root, name.lower(), [], result)
        return result

    def _search_by_name_recursive(self, node, name, path, result):
        if node is None:
            return

        # trái
        self._search_by_name_recursive(node.left, name, path + ['L'], result)

        # so khớp tên
        if node.name.lower() == name:
            result.append((node, self._position_descriptor(path)))

        # phải
        self._search_by_name_recursive(node.right, name, path + ['R'], result)

    # ---------------------------------------------------------
    # 4. TÌM THEO SỐ ĐIỆN THOẠI (O n) + vị trí
    # ---------------------------------------------------------
    def search_by_phone(self, phone):
        result = []
        self._search_by_phone_recursive(self.root, phone, [], result)
        return result

    def _search_by_phone_recursive(self, node, phone, path, result):
        if node is None:
            return

        self._search_by_phone_recursive(node.left, phone, path + ['L'], result)

        if node.phone == phone:
            result.append((node, self._position_descriptor(path)))

        self._search_by_phone_recursive(node.right, phone, path + ['R'], result)

    # ---------------------------------------------------------
    # 5. XÓA KHÁCH HÀNG THEO ID
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
            # Node chỉ có 1 hoặc không có con
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # Node có 2 con: tìm node nhỏ nhất bên phải
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
    # 6. LẤY DANH SÁCH KHÁCH HÀNG THEO THỨ TỰ IN-ORDER
    # ---------------------------------------------------------
    def to_list(self):
        """Trả về danh sách node theo thứ tự In-order để hiển thị."""
        result = []
        self._collect_in_order(self.root, result)
        return result

    def _collect_in_order(self, node, result):
        if node:
            self._collect_in_order(node.left, result)
            result.append(node)
            self._collect_in_order(node.right, result)


    # =============================================================
    #  TRẢ VỀ CẤU TRÚC CÂY ĐỂ VẼ TRÊN HTML
    # =============================================================
    def to_dict(self, node=None):
        if node is None:
            node = self.root
        if node is None:
            return None
        self.print_structure()
        return {
            "id": node.id,
            "name": node.name,
            "phone": node.phone,
            "left": self.to_dict(node.left) if node.left else None,
            "right": self.to_dict(node.right) if node.right else None
        }

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


    # ---------------------------------------------------------
    # 7. HIỂN THỊ SƠ ĐỒ CÂY BINARY TREE (ASCII)
    # ---------------------------------------------------------
    def print_structure(self):
        print("\n===== CẤU TRÚC CÂY NHỊ PHÂN =====")
        self._print_structure_recursive(self.root, "", True)
        print("=================================\n")

    def _print_structure_recursive(self, node, prefix, is_left):
        if node is not None:
            branch = "├── " if is_left else "└── "
            print(prefix + branch + f"[{node.id}] {node.name}")

            self._print_structure_recursive(
                node.left,
                prefix + ("│   " if is_left else "    "),
                True
            )
            self._print_structure_recursive(
                node.right,
                prefix + ("│   " if is_left else "    "),
                False
            )


# =============================================================
#  KHỞI TẠO FLASK APP VÀ CÂY BST
# =============================================================
app = Flask(__name__)
app.secret_key = "super-secret-key"  # để dùng flash message
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

customer_bst = CustomerBST()

# Seed một ít dữ liệu demo
def seed_data():
    customer_bst.insert_auto("Nguyen Van A", "0901234567")
    customer_bst.insert_auto("Tran Thi B", "0988333444")
    customer_bst.insert_auto("Le Van C", "0911222333")
    customer_bst.insert_auto("Pham Thi D", "0933444555")
    customer_bst.insert_auto("Nguyen Van A", "0999888777")
    customer_bst.insert_auto("Pham Thi F", "0977665544")


seed_data()


# =============================================================
#  ROUTES
# =============================================================

# -------------------------------------------------------------
# Trang chính: hiển thị danh sách & form thêm
# -------------------------------------------------------------
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
# Thêm khách hàng
# -------------------------------------------------------------
@app.route("/add", methods=["POST"])
def add_customer():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not phone:
        flash("Tên và số điện thoại không được để trống!", "error")
        return redirect(url_for("index"))

    new_id = customer_bst.insert_auto(name, phone)

    flash(f"Thêm khách hàng ID {new_id} thành công!", "success")
    return redirect(url_for("index"))


# -------------------------------------------------------------
# Xóa khách hàng theo ID
# -------------------------------------------------------------
@app.route("/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    node, _ = customer_bst.search_by_id(customer_id)
    if node:
        customer_bst.delete(customer_id)
        flash(f"Đã xóa khách hàng có ID {customer_id}", "success")
    else:
        flash("Không tìm thấy khách hàng để xóa!", "error")
    return redirect(url_for("index"))


# -------------------------------------------------------------
# Tìm kiếm khách hàng
# -------------------------------------------------------------
@app.route("/search", methods=["POST"])
def search_customer():
    search_type = request.form.get("search_type", "id")
    query = request.form.get("query", "").strip()

    customers = customer_bst.to_list()
    search_results = []

    if not query:
        flash("Vui lòng nhập nội dung cần tìm!", "error")
        return render_template(
            "index.html",
            customers=customers,
            search_results=None,
            search_query="",
            search_type=search_type,
        )

    if search_type == "id":
        try:
            cid = int(query)
        except ValueError:
            flash("ID phải là số!", "error")
            return render_template(
                "index.html",
                customers=customers,
                search_results=None,
                search_query=query,
                search_type=search_type,
            )
        node, pos = customer_bst.search_by_id(cid)
        if node:
            search_results.append({"node": node, "position": pos})
    elif search_type == "name":
        for node, pos in customer_bst.search_by_name(query):
            search_results.append({"node": node, "position": pos})
    elif search_type == "phone":
        for node, pos in customer_bst.search_by_phone(query):
            search_results.append({"node": node, "position": pos})

    if not search_results:
        flash("Không tìm thấy khách hàng phù hợp!", "error")

    return render_template(
        "index.html",
        customers=customers,
        search_results=search_results,
        search_query=query,
        search_type=search_type,
    )


@app.route("/tree")
def show_tree():
    tree = customer_bst.to_dict()
    return render_template("tree.html", tree=tree, steps=None)


@app.route("/tree_search", methods=["POST"])
def tree_search():
    try:
        cid = int(request.form.get("search_id"))
    except:
        cid = None

    tree = customer_bst.to_dict()

    if cid is None:
        return render_template("tree.html", tree=tree, steps=["ID không hợp lệ!"])

    node, steps = customer_bst.search_by_id_with_steps(cid)

    return render_template("tree.html", tree=tree, steps=steps)

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

    added = 0
    for _, row in df.iterrows():
        name = str(row["name"])
        phone = str(row["phone"])
        customer_bst.insert_auto(name, phone)
        added += 1

    flash(f"Đã thêm {added} khách hàng từ file.", "success")
    return redirect(url_for("index"))


# =============================================================
#  CHẠY APP
# =============================================================
if __name__ == "__main__":
    # python app.py
    # Mặc định chạy ở http://127.0.0.1:5000
    app.run(debug=True)
