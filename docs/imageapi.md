# Flog Image WebAPI Document

Both api v1 and api v2 users can follow the following instructions.

/api/v1/image/upload/ or /api/v2/image/upload/

- **POST** Upload Image
  Accepts: *multipart/form-data*

  Status: 201 or 400 or 401

  Args:

  - upload  
  File Type: image object (ends with: .jpg, .png, .gif, .jpeg)

  Example:
  | Key    | Value                |
  | ------ | -------------------- |
  | upload | \<file:picture.png\> |

/api/v1/image/{image_id}

- **DELETE**: Delete an Image
  Args:
  - image_id: **int**
  Status: 204 or 401
