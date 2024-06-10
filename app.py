from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import os
import shutil
from process import *

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):

    # read file from web

    # process file

    # cluster kmean

    # output

    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
    print("SOS")



    try:
        # Lưu file tạm thời
        temp_file_location = f"temp_{file.filename}"
        with open(temp_file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Đảm bảo file được lưu thành công trước khi tiếp tục xử lý
        if not os.path.exists(temp_file_location):
            raise HTTPException(status_code=500, detail="File upload failed")
        print("SOS")
        # Đọc file Excel
        df = pd.read_excel(temp_file_location)

        # Xử lý dữ liệu - Ví dụ: thêm một cột mới với giá trị gấp đôi cột đầu tiên
        df["New Column"] = df.iloc[:, 0] * 2

        # Lưu file Excel đã xử lý
        processed_file_location = f"processed_{file.filename}"
        df.to_excel(processed_file_location, index=False)

        # Đảm bảo file đã xử lý được lưu thành công
        if not os.path.exists(processed_file_location):
            raise HTTPException(status_code=500, detail="Processed file creation failed")

        # Trả lại file Excel đã xử lý
        return FileResponse(processed_file_location, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=processed_file_location)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {e}")

    finally:
        # Xóa file tạm thời
        if os.path.exists(temp_file_location):
            os.remove(temp_file_location)
        # Xóa file đã xử lý sau khi trả về cho người dùng
        # Nếu bạn muốn giữ lại file đã xử lý thì bỏ qua đoạn mã này
        if os.path.exists(processed_file_location):
            os.remove(processed_file_location)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
