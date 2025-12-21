function deleteLinhKien(id) {
    if (!confirm("Bạn có chắc muốn xoá linh kiện này không?")) return;

    fetch(`/api/linhkien/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`lk${id}`).remove();
                alert("Xóa thành công!");
            } else {
                alert(data.message);
            }
        })
        .catch(() => alert("Lỗi kết nối server!"));
}
