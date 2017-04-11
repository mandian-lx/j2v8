%define debug_package  %{nil}
%{?_javapackages_macros:%_javapackages_macros}
%bcond_without nodejs

Summary:	Java Bindings for V8 
Name:		j2v8
Version:	4.5.0
Release:	1
License:	Eclipse Public License
Group:		Development/Java
URL:		https://github.com/eclipsesource/j2v8
Source0:	https://github.com/eclipsesource/J2V8/archive/v%{version}/%{name}-%{version}.tar.gz
Patch1:		%{name}-4.5.0-fix-jni-include-path.patch

# native
%if %{with nodejs}
BuildRequires:	nodejs
BuildRequires:	pkgconfig(libuv)
%endif
BuildRequires:	%{_lib}v8-devel
# java
BuildRequires:	maven-local
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(org.mockito:mockito-all)
%description
J2V8 is a set of Java bindings for V8. J2V8 focuses on performance and
tight integration with V8. It also takes a 'primitive first' approach,
meaning that if a value can be accessed as a primitive, then it should be.
This forces a more static type system between the JS and Java code, but it
also improves the performance since intermediate Objects are not created.

%files -f .mfiles
%{_jnidir}/lib%{name}_linux_%{_arch}.so
%doc README.md
%doc epl-v10.html

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc
%doc epl-v10.html

#----------------------------------------------------------------------------

%prep
%setup -q -n J2V8-%{version}

# Delete prebuild JARs
find . -name "*.jar" -delete
find . -name "*.class" -delete

# Apply all patches
%patch1 -p1 -b .natives

# fix arch
sed -i -e "s|\${os}|linux|g" -e "s|\${arch}|%{_arch}|g" pom.xml
%pom_xpath_replace pom:arch '<arch>%{_arch}</arch>' .

%build
# native
%setup_compile_flags
pushd jni
${CXX} %{optflags} -std=c++11 \
	-I /usr/lib/jvm/java-1.8.0/include/ \
	-I /usr/lib/jvm/java-1.8.0/include/linux/ \
%if %{with nodejs}
	-D NODE_COMPATIBLE=1 \
	`pkg-config --libs libuv` \
%endif
	-lv8 -lv8_libbase -lv8_libplatform \
	-fPIC   -lrt -shared -o libj2v8_linux_%{_arch}.so \
	com_eclipsesource_v8_V8Impl.cpp
popd

# java
%mvn_build -f

%install
%mvn_install

# natives
install -dm 0755 %{buildroot}%{_jnidir}/
install -pm 0755 jni/lib%{name}_linux_%{_arch}.so %{buildroot}%{_jnidir}/

