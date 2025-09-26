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
        sys.exit(1)
    
    # 读取docker-compose文件
    with open(compose_file, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"错误: 解析YAML文件时出错: {e}")
            sys.exit(1)
    
    # 检查services是否存在
    if 'services' in data:
        # 过滤服务，只保留有build或image字段的服务
        filtered_services = {}
        for service_name, service_config in data['services'].items():
            if 'build' in service_config or 'image' in service_config:
                filtered_services[service_name] = service_config
            else:
                print(f'移除服务 {service_name}，因为它既没有build也没有image字段')
        
        # 更新services
        data['services'] = filtered_services
        
        # 写入处理后的文件
        with open(compose_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"成功处理 {compose_file}，保留了 {len(filtered_services)} 个服务")
    else:
        print("警告: 文件中没有找到services字段")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python filter-compose-services.py <compose-file>")
        sys.exit(1)
    
    filter_services(sys.argv[1])