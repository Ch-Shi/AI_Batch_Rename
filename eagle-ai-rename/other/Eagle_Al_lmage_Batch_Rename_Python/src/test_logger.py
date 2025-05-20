from utils.enhanced_logger import enhanced_logger, LogType
import time

def test_enhanced_logger():
    print("开始测试增强日志系统...")
    
    # 测试基本日志功能
    enhanced_logger.log_success("这是一条成功信息", context="metadata_updated")
    enhanced_logger.log_error("这是一条错误信息", error="测试错误", context="image_analysis_error")
    enhanced_logger.log_warning("这是一条警告信息", context="name_collision")
    
    # 测试图像处理相关功能
    enhanced_logger.log_image_analysis(
        folder="test_folder", 
        main_img="test_image.png", 
        result={"description": "测试名称"}, 
        group_id="TEST001"
    )
    
    # 测试重命名功能
    enhanced_logger.log_rename(
        "主图", 
        "old_image.png", 
        "new_image.png", 
        success=True, 
        group_id="TEST001"
    )
    
    # 测试元数据更新
    enhanced_logger.log_metadata_update(
        "metadata.json", 
        "old_name", 
        "new_name", 
        success=True, 
        group_id="TEST001"
    )
    
    # 测试恢复操作
    enhanced_logger.log_recovery_operation(
        "主图", 
        "main_image.png", 
        "old_name", 
        "new_name", 
        success=True, 
        group_id="TEST001"
    )
    
    # 测试完整流程
    enhanced_logger.log(
        LogType.INFO,
        "开始处理测试图片",
        context="process_start",
        file_path="test/image.png",
        is_console=True
    )
    
    # 模拟处理时间
    time.sleep(1)
    
    # 完成会话
    stats = enhanced_logger.finish_session(
        total_images=100,
        processed_images=90,
        skipped_images=8,
        deleted_images=2
    )
    
    print("日志测试完成，请检查 logs 目录查看生成的日志文件!")
    return stats

if __name__ == "__main__":
    test_enhanced_logger() 