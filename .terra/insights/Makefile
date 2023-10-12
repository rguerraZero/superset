AWS_REGION:=$(if $(AWS_REGION),$(AWS_REGION),us-west-2)
ENVIRONMENT:=qa
GIT_SHA="$(shell git rev-parse --short=7 HEAD)"
TERRAFORM:=terraform
S3_BUCKET_PREFIX:=$(if $(S3_BUCKET_PREFIX),$(S3_BUCKET_PREFIX),zf-terraform)

tf_files := $(shell find . -name "*.tf")

all: plan

check-fmt:
	$(TERRAFORM) fmt -check=true

format:
	$(TERRAFORM) fmt

init:
	$(TERRAFORM) init \
		-backend-config="bucket=$(S3_BUCKET_PREFIX)-$(ENVIRONMENT)" \
		-backend-config="region=$(AWS_REGION)"

validate: ${tf_files}
	$(TERRAFORM) validate

plan: .terraform/terraform.tfstate ${tf_files}
	TF_LOG=TRACE && $(TERRAFORM) plan \
		-var "env=$(ENVIRONMENT)" \
		-var "git_sha=$(GIT_SHA)" \
		-out terra.plan

apply: plan
	TF_LOG=TRACE && $(TERRAFORM) apply terra.plan

clean:
	rm -f *.backup *.plan
	rm -f .terraform/terraform.tfstate

clobber: clean
	rm -rf .terraform

plan_destroy: .terraform/terraform.tfstate ${tf_files}
	$(TERRAFORM) plan -destroy \
		-var "env=$(ENVIRONMENT)" \
		-var "git_sha=$(GIT_SHA)" \
		-out terra_destroy.plan

destroy: plan_destroy
	$(TERRAFORM) destroy \
		-var "env=$(ENVIRONMENT)" \
		-var "git_sha=$(GIT_SHA)" \
		-auto-approve

.PHONY: all check-fmt format init validate plan apply clean clobber destroy plan_destroy