resource "helm_release" "jenkins-wrapper" {
  name       = "jenkins-wrapper"
  chart      = "/chart"
  namespace  = "jenkins-wrapper-ns"
  create_namespace = true
}