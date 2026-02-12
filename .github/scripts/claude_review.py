#!/usr/bin/env python3
"""
Claude AI를 사용한 자동 코드 리뷰 스크립트
버그, 보안 취약점, 성능 문제, 코드 품질을 검토합니다.
"""

import os
import json
import re
from anthropic import Anthropic
from github import Github

# 환경 변수 설정
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
PR_NUMBER = int(os.getenv('PR_NUMBER'))
REPO_NAME = os.getenv('REPO_NAME')

# 클라이언트 초기화
claude = Anthropic(api_key=ANTHROPIC_API_KEY)
github = Github(GITHUB_TOKEN)
repo = github.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)


def get_pr_diff():
    """PR의 변경사항을 가져옵니다."""
    try:
        with open('pr_diff.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading diff: {e}")
        return ""


def create_review_prompt(diff_content):
    """코드 리뷰를 위한 프롬프트를 생성합니다."""
    return f"""당신은 숙련된 시니어 개발자로서 코드 리뷰를 수행합니다.
다음 Pull Request의 변경사항을 철저히 검토하고, 아래 항목들에 대해 분석해주세요:

## 검토 항목:
1. **버그 및 잠재적 오류**: 논리 오류, null 참조, 타입 불일치, 예외 처리 누락 등
2. **보안 취약점**: SQL injection, XSS, CSRF, 인증/인가 문제, 민감 정보 노출 등
3. **성능 최적화**: 비효율적인 알고리즘, N+1 쿼리, 메모리 누수, 불필요한 연산 등
4. **코드 품질 및 베스트 프랙티스**:
   - 가독성과 유지보수성
   - 적절한 추상화와 모듈화
   - 코드 중복 제거
   - 네이밍 컨벤션
   - 주석과 문서화
   - 테스트 커버리지

## Pull Request 변경사항:
```diff
{diff_content}
```

## 응답 형식:
다음 JSON 형식으로 응답해주세요:

{{
  "summary": "전반적인 코드 품질 평가 (1-2문장)",
  "severity": "critical|high|medium|low|info",
  "issues": [
    {{
      "category": "bug|security|performance|quality",
      "severity": "critical|high|medium|low",
      "title": "문제 제목",
      "description": "상세 설명",
      "file": "파일 경로 (있다면)",
      "line": 라인 번호 (있다면, 숫자),
      "suggestion": "개선 제안",
      "code_example": "개선된 코드 예시 (있다면)"
    }}
  ],
  "strengths": ["잘한 점들"],
  "recommendations": ["전반적인 개선 제안"]
}}

**중요**:
- 실제 문제가 있을 때만 issues에 포함하세요.
- 심각도는 정확하게 평가해주세요.
- 구체적이고 실행 가능한 제안을 해주세요.
- 한국어로 작성해주세요."""


def review_code_with_claude(diff_content):
    """Claude API를 사용하여 코드를 리뷰합니다."""
    try:
        prompt = create_review_prompt(diff_content)

        message = claude.messages.create(
            model="claude-sonnet-4-20250514",  # 최신 모델 사용
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        # JSON 추출 (마크다운 코드 블록 안에 있을 수 있음)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        review_data = json.loads(response_text)
        return review_data

    except Exception as e:
        print(f"Error during Claude API call: {e}")
        return {
            "summary": f"리뷰 중 오류 발생: {str(e)}",
            "severity": "info",
            "issues": [],
            "strengths": [],
            "recommendations": []
        }


def format_review_comment(review_data):
    """리뷰 결과를 GitHub 코멘트 형식으로 변환합니다."""
    severity_emoji = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "⚡",
        "low": "💡",
        "info": "ℹ️"
    }

    category_emoji = {
        "bug": "🐛",
        "security": "🔒",
        "performance": "⚡",
        "quality": "✨"
    }

    comment = f"""## 🤖 Claude AI 코드 리뷰

{severity_emoji.get(review_data['severity'], 'ℹ️')} **전체 평가**: {review_data['summary']}

---

"""

    # 발견된 이슈들
    if review_data.get('issues'):
        issues_by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        for issue in review_data['issues']:
            severity = issue.get('severity', 'low')
            issues_by_severity[severity].append(issue)

        comment += "### 📋 발견된 이슈\n\n"

        for severity in ['critical', 'high', 'medium', 'low']:
            issues = issues_by_severity[severity]
            if issues:
                comment += f"#### {severity_emoji[severity]} {severity.upper()}\n\n"

                for i, issue in enumerate(issues, 1):
                    category = issue.get('category', 'quality')
                    comment += f"{i}. {category_emoji.get(category, '📝')} **{issue['title']}**\n"

                    if issue.get('file'):
                        location = f"`{issue['file']}`"
                        if issue.get('line'):
                            location += f" (L{issue['line']})"
                        comment += f"   - 위치: {location}\n"

                    comment += f"   - 설명: {issue['description']}\n"

                    if issue.get('suggestion'):
                        comment += f"   - 💡 제안: {issue['suggestion']}\n"

                    if issue.get('code_example'):
                        comment += f"   - 개선 예시:\n```\n{issue['code_example']}\n```\n"

                    comment += "\n"
    else:
        comment += "### ✅ 이슈 없음\n\n특별한 문제가 발견되지 않았습니다.\n\n"

    # 잘한 점들
    if review_data.get('strengths'):
        comment += "### 👍 잘한 점\n\n"
        for strength in review_data['strengths']:
            comment += f"- {strength}\n"
        comment += "\n"

    # 추가 권장사항
    if review_data.get('recommendations'):
        comment += "### 💭 권장사항\n\n"
        for rec in review_data['recommendations']:
            comment += f"- {rec}\n"
        comment += "\n"

    comment += "---\n\n"
    comment += "*🤖 이 리뷰는 Claude AI (Sonnet 4.5)가 자동으로 생성했습니다.*\n"
    comment += "*💬 궁금한 점이 있으시면 댓글로 남겨주세요!*"

    return comment


def post_review_to_pr(review_comment):
    """GitHub PR에 리뷰 코멘트를 게시합니다."""
    try:
        # 기존 Claude 리뷰 찾기
        comments = pr.get_issue_comments()
        existing_review = None

        for comment in comments:
            if "🤖 Claude AI 코드 리뷰" in comment.body:
                existing_review = comment
                break

        if existing_review:
            # 기존 리뷰 업데이트
            existing_review.edit(review_comment)
            print("✅ 기존 리뷰를 업데이트했습니다.")
        else:
            # 새 리뷰 작성
            pr.create_issue_comment(review_comment)
            print("✅ 새 리뷰를 작성했습니다.")

    except Exception as e:
        print(f"❌ GitHub에 코멘트를 게시하는 중 오류 발생: {e}")


def save_review_results(review_data):
    """리뷰 결과를 파일로 저장합니다."""
    try:
        with open('review_results.json', 'w', encoding='utf-8') as f:
            json.dump(review_data, f, ensure_ascii=False, indent=2)
        print("✅ 리뷰 결과를 저장했습니다.")
    except Exception as e:
        print(f"⚠️ 리뷰 결과 저장 중 오류: {e}")


def main():
    """메인 함수"""
    print("🚀 Claude AI 코드 리뷰를 시작합니다...")

    # 1. PR diff 가져오기
    print("📥 PR 변경사항을 가져오는 중...")
    diff_content = get_pr_diff()

    if not diff_content or diff_content.strip() == "":
        print("⚠️ 변경사항이 없거나 가져오는데 실패했습니다.")
        return

    print(f"✅ {len(diff_content)} 글자의 변경사항을 가져왔습니다.")

    # 2. Claude로 코드 리뷰
    print("🔍 Claude AI가 코드를 분석하는 중...")
    review_data = review_code_with_claude(diff_content)

    # 3. 리뷰 결과 저장
    save_review_results(review_data)

    # 4. GitHub PR에 코멘트 작성
    print("💬 GitHub PR에 리뷰를 게시하는 중...")
    review_comment = format_review_comment(review_data)
    post_review_to_pr(review_comment)

    # 5. 결과 출력
    print("\n" + "="*60)
    print("📊 리뷰 요약:")
    print(f"   전체 평가: {review_data['summary']}")
    print(f"   심각도: {review_data['severity']}")
    print(f"   발견된 이슈: {len(review_data.get('issues', []))}개")
    print("="*60)
    print("\n✅ 코드 리뷰가 완료되었습니다!")


if __name__ == "__main__":
    main()
