# Claude AI 자동 코드 리뷰 설정 가이드

## 🎯 개요

이 시스템은 Pull Request가 생성되거나 업데이트될 때 자동으로 Claude AI를 사용하여 코드를 검토합니다.

**검토 항목:**
- 🐛 버그 및 잠재적 오류
- 🔒 보안 취약점
- ⚡ 성능 최적화 기회
- ✨ 코드 품질 및 베스트 프랙티스

---

## 📋 설정 방법

### 1️⃣ Claude API 키 발급받기

1. [Anthropic Console](https://console.anthropic.com/) 접속
2. 로그인 후 **API Keys** 메뉴로 이동
3. **Create Key** 버튼 클릭
4. API 키 복사 (한 번만 표시되므로 안전하게 보관!)

### 2️⃣ GitHub Secrets에 API 키 등록

1. GitHub 저장소 페이지로 이동
2. **Settings** → **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 버튼 클릭
4. 다음 정보 입력:
   - Name: `ANTHROPIC_API_KEY`
   - Secret: (복사한 Claude API 키 붙여넣기)
5. **Add secret** 클릭

### 3️⃣ 변경사항 커밋 및 푸시

```bash
cd /home/sangchul/ssjang617

# 변경사항 확인
git status

# 파일 스테이징
git add .github/

# 커밋
git commit -m "feat: Add Claude AI automated code review

- GitHub Actions workflow for PR reviews
- Python script using Claude Sonnet 4.5
- Comprehensive analysis: bugs, security, performance, quality

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 원격 저장소에 푸시
git push
```

---

## 🚀 사용 방법

### 자동 실행

Pull Request를 생성하거나 업데이트하면 자동으로 실행됩니다:

1. 브랜치를 만들고 코드를 수정
2. GitHub에 푸시
3. Pull Request 생성
4. 자동으로 Claude AI가 코드 리뷰 시작!
5. 리뷰 완료 후 PR에 코멘트로 결과 표시

### 예시 워크플로우

```bash
# 새 브랜치 생성
git checkout -b feature/new-feature

# 코드 수정
# ... 코딩 작업 ...

# 커밋 및 푸시
git add .
git commit -m "feat: Add new feature"
git push -u origin feature/new-feature

# GitHub에서 PR 생성
gh.exe pr create --title "Add new feature" --body "Description of changes"

# 자동으로 Claude AI 리뷰가 시작됩니다!
```

---

## 📊 리뷰 결과 형식

리뷰 결과는 다음과 같이 표시됩니다:

```
## 🤖 Claude AI 코드 리뷰

⚠️ **전체 평가**: [전반적인 평가 내용]

---

### 📋 발견된 이슈

#### 🚨 CRITICAL
1. 🔒 **[보안 문제 제목]**
   - 위치: `파일경로` (L123)
   - 설명: [문제 설명]
   - 💡 제안: [개선 방안]

#### ⚠️ HIGH
...

### 👍 잘한 점
- [칭찬할 점들]

### 💭 권장사항
- [추가 개선 제안]
```

---

## 🔧 커스터마이징

### 검토 강도 조절

`.github/scripts/claude_review.py` 파일에서 프롬프트를 수정하여 검토 강도나 초점을 조절할 수 있습니다:

```python
def create_review_prompt(diff_content):
    # 프롬프트 수정하여 검토 방식 변경 가능
    ...
```

### 다른 모델 사용

더 빠른 응답이 필요하면 `claude-haiku-3-5` 모델을 사용할 수 있습니다:

```python
message = claude.messages.create(
    model="claude-haiku-3-5-20241022",  # 더 빠르고 저렴한 모델
    ...
)
```

### 특정 파일만 검토

워크플로우 파일에서 `paths` 필터를 추가할 수 있습니다:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'src/**'
      - '**.py'
      - '**.js'
```

---

## 💰 비용 안내

Claude API 사용 비용은 입력/출력 토큰 수에 따라 결정됩니다:

- **Claude Sonnet 4.5**: $3/M 입력 토큰, $15/M 출력 토큰
- **Claude Haiku 3.5**: $0.80/M 입력 토큰, $4/M 출력 토큰

평균적인 PR 리뷰 (2000줄 코드):
- 입력: ~10,000 토큰 = $0.03
- 출력: ~2,000 토큰 = $0.03
- **총 비용: ~$0.06 per review**

[Anthropic Pricing](https://www.anthropic.com/pricing) 참고

---

## ❓ 문제 해결

### API 키 오류

```
Error: ANTHROPIC_API_KEY is not set
```

→ GitHub Secrets에 `ANTHROPIC_API_KEY`가 올바르게 설정되었는지 확인

### GitHub Token 권한 오류

```
Error: Resource not accessible by integration
```

→ 워크플로우 파일의 `permissions` 섹션 확인

### 리뷰가 작동하지 않음

1. **Actions 탭** 에서 워크플로우 실행 로그 확인
2. 실패한 단계의 상세 로그 확인
3. API 사용량 제한 확인

---

## 📚 참고 자료

- [Claude API Documentation](https://docs.anthropic.com/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)

---

## 🤝 기여하기

이 시스템을 개선하고 싶으시다면:

1. 이슈를 생성하거나
2. Pull Request를 보내주세요!

(그러면 Claude AI가 자동으로 리뷰해드립니다! 😄)
