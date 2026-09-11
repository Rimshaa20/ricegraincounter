import os
from rice_counter import count_rice_grains

d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_images")
for name in os.listdir(d):
    if not name.endswith(".jpg"):
        continue
    path = os.path.join(d, name)
    with open(path, "rb") as f:
        data = f.read()
    try:
        r = count_rice_grains(data)
        print(name, "=> count:", r["total_count"], "|", r["message"])
        out = os.path.join(d, "annotated_" + name)
        with open(out, "wb") as f:
            f.write(r["annotated_image_bytes"])
        print("   annotated->", out)
    except Exception as e:
        print(name, "=> ERROR:", e)