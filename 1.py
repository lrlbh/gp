import sys

def main():
    # 检查参数个数，至少要有两个数字
    if len(sys.argv) < 3:
        print("用法：python calculate_discount.py <原价> <现价>")
        print("示例：python calculate_discount.py 1.86 1.83")
        sys.exit(1)

    try:
        old_price = float(sys.argv[1])
        new_price = float(sys.argv[2])
    except ValueError:
        print("错误：请输入有效的数字")
        sys.exit(1)

    if old_price == 0:
        print("原价不能为零，无法计算降幅")
        sys.exit(1)

    decrease = old_price - new_price
    percent = (decrease / old_price) * 100

    # print(f"原价：{old_price}")
    # print(f"现价：{new_price}")
    # print(f"减少数值：{decrease:.4f}")   # 保留4位小数
    print(f" --> {new_price} 降幅：{percent:.2f}%")

if __name__ == "__main__":
    main()

