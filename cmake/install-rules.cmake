install(
    TARGETS vayunicus_exe
    RUNTIME COMPONENT vayunicus_Runtime
)

if(PROJECT_IS_TOP_LEVEL)
  include(CPack)
endif()
