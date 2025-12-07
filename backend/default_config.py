"""
Default API Configuration
系统采用前端配置优先的设计，不再依赖后端环境变量。
推荐使用中转API: https://apipro.maynor1024.live/
"""

# 默认为空，强制用户通过前端界面配置 API 密钥
# 推荐使用中转API，在前端设置界面中选择 "中转API（推荐）" 预设
DEFAULT_TEXT_API_KEY = ""
DEFAULT_TEXT_API_BASE = "https://apipro.maynor1024.live"

DEFAULT_IMAGE_API_KEY = ""
DEFAULT_IMAGE_API_BASE = "https://apipro.maynor1024.live"

# Built-in MinerU token for document parsing
# Get yours at: https://mineru.net
DEFAULT_MINERU_TOKEN = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI3MzQwMDc1NyIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NTA3ODU5NiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTMzNDY0MDgzMDYiLCJvcGVuSWQiOm51bGwsInV1aWQiOiIxZjEyZjZhYy0xMmU1LTQ4OWUtODlmMC0xNjhiMGMzOTJlNDQiLCJlbWFpbCI6IiIsImV4cCI6MTc2NjI4ODE5Nn0.pQP77iUZOo9JrDKqvnCeULMFP6bPsu-imbdf2CB5kU6ECVBIZ3_8cbaXBBehRyc8sJjAFetS4vQgIDRvvecyTA"
DEFAULT_MINERU_API_BASE = "https://mineru.net"

# 配置说明：
# 1. 首次使用时，访问前端页面右上角的 "设置" 按钮
# 2. 选择 "中转API（推荐）" 预设，使用 https://apipro.maynor1024.live/
# 3. 输入您的 API Key（格式如 sk-xxx）
# 4. 保存配置即可开始使用
