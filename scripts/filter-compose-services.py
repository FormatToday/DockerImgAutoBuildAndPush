#!/usr/bin/env python3
"""
过滤docker-compose.yml文件中的服务，只保留包含build或image字段的服务
"""

import yaml
import sys
import os

def filter_services(compose_file):
    """过滤服务，只保留有build或image字段的服务"""
    # 检查文件是否存在
    if not os.path.exists(compose_file):
        print(f"错误: 文件 {compose_file} 不存在")
        return False
    
    # 读取docker-compose文件
    try:
        with open(compose_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"错误: 文件 {compose_file} 未找到")
        return False
    except yaml.YAMLError as e:
        print(f"错误: 解析YAML文件时出错: {e}")
        return False
    except Exception as e:
        print(f"错误: 读取文件时发生未知错误: {e}")
        return False
    
    # 检查是否为空文件
    if data is None:
        print("警告: 文件为空")
        return False
    
    # 检查services是否存在
    if 'services' not in data:
        print("警告: 文件中没有找到services字段")
        return False
    
    # 过滤服务，只保留有build或image字段的服务
    original_count = len(data['services'])
    filtered_services = {}
    
    for service_name, service_config in data['services'].items():
        # 确保service_config是字典类型
        if not isinstance(service_config, dict):
            print(f"警告: 服务 {service_name} 的配置不是字典类型，将被移除")
            continue
            
        if 'build' in service_config or 'image' in service_config:
            filtered_services[service_name] = service_config
        else:
            print(f"移除服务 {service_name}，因为它既没有build也没有image字段")
    
    # 更新services
    data['services'] = filtered_services
    
    # 写入处理后的文件
    try:
        with open(compose_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        filtered_count = len(filtered_services)
        print(f"成功处理 {compose_file}")
        print(f"原始服务数: {original_count}")
        print(f"保留服务数: {filtered_count}")
        print(f"移除服务数: {original_count - filtered_count}")
        return True
    except Exception as e:
        print(f"错误: 写入文件时发生错误: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python filter-compose-services.py <compose-file>")
        print("示例: python filter-compose-services.py docker-compose.yml")
        return 1
    
    success = filter_services(sys.argv[1])
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())