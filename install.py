import launch

if not launch.is_installed("pillow"):
    launch.run_pip("install pillow", "requirement for Gaussian Blur and Vignette")