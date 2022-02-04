#!/bin/bash -e

if [[ -z ${GITHUB_TOKEN} ]]
then
    echo "GITHUB_TOKEN was not provided"
    exit 1
fi

if [[ ${GITHUB_EVENT_NAME} != "pull_request" ]]
then
    echo "This action runs only on pull request events"
    exit 1
fi

github_pr_url=`jq '.pull_request.url' ${GITHUB_EVENT_PATH}`
# remove leading and trailing quotes
github_pr_url=`sed -e 's/^"//' -e 's/"$//' <<<"$github_pr_url"`

echo "Looking for diff at ${github_pr_url}"
curl --request GET --url ${github_pr_url} --header "authorization: Bearer ${GITHUB_TOKEN}" --header "Accept: application/vnd.github.v3.diff" > github_diff.txt
diff_length=`wc -l github_diff.txt`

echo "GITHUB DIFF FILE: "
cat github_diff.txt

echo "Approximate diff size: ${diff_length}"
python_files=`cat github_diff.txt | grep -E -- "\+\+\+ |\-\-\- " | awk '{print $2}' | grep -Po -- "(?<=[ab]/).+\.py$"`
echo "Changed files: ${python_files}"

if [[ -z "${LINE_LENGTH}" ]]; then
    line_length=120
else
    line_length="${LINE_LENGTH}"
fi

echo "Running isort"
isort --check-only --quiet ${python_files}
echo "Running black"
black --line-length ${line_length} --check ${python_files}
