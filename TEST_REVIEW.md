# Claude AI 자동 리뷰 테스트

이 파일은 Claude AI 자동 코드 리뷰 시스템을 테스트하기 위해 만들어졌습니다.

## 테스트 코드 예시

```python
def calculate_sum(a, b):
    # 간단한 덧셈 함수
    result = a + b
    return result

def divide_numbers(x, y):
    # 나눗셈 함수 (버그 포함!)
    return x / y  # ZeroDivisionError 가능성!

# 보안 취약점 예시
password = "hardcoded_password_123"  # 하드코딩된 비밀번호!

# 성능 문제 예시
def slow_function():
    result = []
    for i in range(1000):
        for j in range(1000):  # O(n²) - 비효율적!
            result.append(i * j)
    return result
```

Claude AI가 이 코드의 문제점들을 찾아낼 수 있을까요? 🤔
