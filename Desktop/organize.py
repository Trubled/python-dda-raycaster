import os
import shutil

# Target directory (your desktop)
path = os.path.expanduser("~/Desktop")

# Define file categories
extensions = {
	"images": [".png", ".jpg", ".jpeg", ".gif"],
	"Documents": [".pdf", ".docx", ".txt", ".xlsx"],
	"Code": [".py", ".html", ".js", ".css"]
}

print("Organizing desktop...")
# (We can add the sorting logic next!)