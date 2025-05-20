import os
import json
import logging
from datetime import datetime
from enum import Enum
from colorama import Fore, Style

class LogType(Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    RECOVERY = "RECOVERY"
    STATS = "STATS"

class EnhancedLogger:
    def __init__(self, log_dir="logs"):
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 当前会话的唯一标识
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 日志文件路径
        self.detailed_log = os.path.join(log_dir, f"eagle_rename_{self.session_id}_detailed.log")
        self.error_log = os.path.join(log_dir, f"eagle_rename_{self.session_id}_errors.log")
        self.success_log = os.path.join(log_dir, f"eagle_rename_{self.session_id}_success.log")
        self.stats_log = os.path.join(log_dir, f"eagle_rename_{self.session_id}_stats.log")
        
        # 错误统计
        self.error_counts = {
            "metadata_read_error": 0,
            "image_analysis_error": 0,
            "metadata_write_error": 0,
            "main_image_rename_error": 0,
            "thumb_image_rename_error": 0,
            "recovery_error": 0,
            "other_error": 0
        }
        
        # 成功统计
        self.success_counts = {
            "total_processed": 0,
            "metadata_updated": 0,
            "main_image_renamed": 0,
            "thumb_image_renamed": 0,
            "skipped_images": 0,
            "deleted_images": 0
        }
        
        # 初始化日志
        self._init_logs()
        
    def _init_logs(self):
        """初始化日志文件，写入头部信息"""
        session_start = {
            "event": "session_start",
            "timestamp": self._get_timestamp(),
            "session_id": self.session_id,
            "message": "Eagle重命名会话开始"
        }
        
        # 写入会话开始标记到所有日志
        self._write_to_log(self.detailed_log, session_start)
        self._write_to_log(self.error_log, session_start)
        self._write_to_log(self.success_log, session_start)
        
    def _get_timestamp(self):
        """获取当前精确时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
    def _write_to_log(self, log_file, data):
        """写入日志到指定文件"""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
    def log(self, log_type, message, context=None, error=None, file_path=None, group_id=None,
            old_name=None, new_name=None, is_console=True):
        """记录日志"""
        timestamp = self._get_timestamp()
        
        # 构建基本日志内容
        log_entry = {
            "timestamp": timestamp,
            "type": log_type.value,
            "message": message
        }
        
        # 添加上下文信息
        if context:
            log_entry["context"] = context
        if error:
            log_entry["error"] = str(error)
        if file_path:
            log_entry["file_path"] = file_path
        if group_id:
            log_entry["group_id"] = group_id
        if old_name:
            log_entry["old_name"] = old_name
        if new_name:
            log_entry["new_name"] = new_name
            
        # 记录到详细日志
        self._write_to_log(self.detailed_log, log_entry)
        
        # 按类型记录到对应日志
        if log_type == LogType.ERROR or log_type == LogType.RECOVERY:
            self._write_to_log(self.error_log, log_entry)
            # 更新错误统计
            error_type = context if context else "other_error"
            if error_type in self.error_counts:
                self.error_counts[error_type] += 1
            else:
                self.error_counts["other_error"] += 1
                
        elif log_type == LogType.SUCCESS:
            self._write_to_log(self.success_log, log_entry)
            # 更新成功统计
            if context in self.success_counts:
                self.success_counts[context] += 1
                
        # 控制台输出
        if is_console:
            color = Fore.WHITE
            if log_type == LogType.SUCCESS:
                color = Fore.GREEN
            elif log_type == LogType.ERROR:
                color = Fore.RED
            elif log_type == LogType.WARNING:
                color = Fore.YELLOW
            elif log_type == LogType.RECOVERY:
                color = Fore.CYAN
                
            console_msg = f"{color}{message}{Style.RESET_ALL}"
            if error:
                console_msg += f" | {Fore.RED}错误: {error}{Style.RESET_ALL}"
                
            print(console_msg)
                
    def log_success(self, message, context=None, **kwargs):
        """记录成功信息"""
        self.log(LogType.SUCCESS, message, context, **kwargs)
        
    def log_error(self, message, error=None, context=None, **kwargs):
        """记录错误信息"""
        self.log(LogType.ERROR, message, context, error, **kwargs)
        
    def log_warning(self, message, context=None, **kwargs):
        """记录警告信息"""
        self.log(LogType.WARNING, message, context, **kwargs)
        
    def log_recovery(self, message, error=None, context=None, **kwargs):
        """记录恢复操作信息"""
        self.log(LogType.RECOVERY, message, context, error, **kwargs)
        
    def log_image_analysis(self, folder, main_img, result=None, error=None, group_id=None):
        """记录图像分析结果"""
        if error:
            self.log_error(
                f"图像分析失败: {os.path.basename(main_img)}",
                error=error,
                context="image_analysis_error",
                file_path=main_img,
                group_id=group_id
            )
        else:
            self.log_success(
                f"图像分析成功: {os.path.basename(main_img)}",
                context="image_analyzed",
                file_path=main_img,
                group_id=group_id
            )
            # 记录详细分析结果到日志(不在控制台显示)
            if result:
                self.log(
                    LogType.DEBUG, 
                    "图像分析详细结果", 
                    context="image_analysis_result",
                    file_path=main_img,
                    group_id=group_id,
                    is_console=False
                )
    
    def log_rename(self, operation_type, old_path, new_path, success=True, error=None, group_id=None):
        """记录重命名操作"""
        old_name = os.path.basename(old_path)
        new_name = os.path.basename(new_path)
        
        if success:
            self.log_success(
                f"{operation_type}重命名成功: {old_name} -> {new_name}",
                context=f"{operation_type.lower()}_image_renamed",
                file_path=new_path,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
        else:
            self.log_error(
                f"{operation_type}重命名失败: {old_name}",
                error=error,
                context=f"{operation_type.lower()}_image_rename_error",
                file_path=old_path,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
    
    def log_metadata_update(self, meta_path, old_name, new_name, success=True, error=None, group_id=None):
        """记录元数据更新操作"""
        if success:
            self.log_success(
                f"更新元数据成功: {old_name} -> {new_name}",
                context="metadata_updated",
                file_path=meta_path,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
        else:
            self.log_error(
                f"更新元数据失败: {meta_path}",
                error=error,
                context="metadata_write_error",
                file_path=meta_path,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
    
    def log_recovery_operation(self, operation_type, path, old_name, new_name, success=True, error=None, group_id=None):
        """记录恢复操作"""
        if success:
            self.log_recovery(
                f"恢复{operation_type}成功: {new_name} -> {old_name}",
                context=f"recovery_{operation_type.lower()}",
                file_path=path,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
        else:
            self.log_error(
                f"恢复{operation_type}失败: {path}",
                error=error,
                context="recovery_error",
                file_path=path,
                old_name=old_name,
                new_name=new_name,
                group_id=group_id
            )
    
    def finish_session(self, total_images, processed_images, skipped_images, deleted_images):
        """记录会话结束与统计信息"""
        # 更新统计信息
        self.success_counts["total_processed"] = processed_images
        self.success_counts["skipped_images"] = skipped_images
        self.success_counts["deleted_images"] = deleted_images
        
        # 构建统计信息
        stats = {
            "event": "session_end",
            "timestamp": self._get_timestamp(),
            "session_id": self.session_id,
            "duration": "",  # 可以增加会话持续时间计算
            "summary": {
                "total_images": total_images,
                "processed_images": processed_images,
                "skipped_images": skipped_images,
                "deleted_images": deleted_images
            },
            "success_stats": self.success_counts,
            "error_stats": self.error_counts
        }
        
        # 记录统计信息
        self._write_to_log(self.detailed_log, stats)
        self._write_to_log(self.stats_log, stats)
        
        # 控制台输出
        print(f"\n{Fore.GREEN}会话统计:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}总图片数：{total_images}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}已处理：{processed_images}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}已跳过：{skipped_images}（不在目标目录中）{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}已删除：{deleted_images}（标记为删除的图片）{Style.RESET_ALL}")
        
        # 错误统计
        total_errors = sum(self.error_counts.values())
        if total_errors > 0:
            print(f"\n{Fore.RED}错误统计:{Style.RESET_ALL}")
            for error_type, count in self.error_counts.items():
                if count > 0:
                    print(f"{Fore.RED}{error_type}: {count}{Style.RESET_ALL}")
        
        return stats

# 创建全局日志实例
enhanced_logger = EnhancedLogger() 