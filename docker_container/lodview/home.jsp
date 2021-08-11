<%@page session="true"%><%@taglib uri="http://www.springframework.org/tags" prefix="sp"%><%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%><html version="XHTML+RDFa 1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/1999/xhtml http://www.w3.org/MarkUp/SCHEMA/xhtml-rdfa-2.xsd" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:xsd="http://www.w3.org/2001/XMLSchema#" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:foaf="http://xmlns.com/foaf/0.1/">
<head data-color="${colorPair}" profile="http://www.w3.org/1999/xhtml/vocab">
<title>${results.getTitle()}&mdash;LodView</title>
<jsp:include page="inc/header.jsp"></jsp:include>
</head>
<body id="top">
	<article>
		<div id="logoBanner">
			<div id="logo">
				<!-- placeholder for logo -->
			</div>
		</div>
		<header>
			<hgroup>
				<h1>
					<span>Translation Coherence</span>
				</h1>
				<h2>
					<span>An ontology to describe language constructs in order to compare machine-generated ontologies.</span>
				</h2>
			</hgroup>
			<div id="abstract">
				<div class="value">It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.</div>
			</div>

		</header>

		<aside class="empty"></aside>

		<div id="directs">

			<div class="value">Here are the ontologies that can be browsed:
				<a href="http://localhost:8080/lodview/vocabulary.ttl">vocabulary.ttl</a> - the vocabulary for making statements to compare two given ontologies.
				<br>
				<b>sources</b>: the example source ontologies to be compared
				<i>original (english)</i>
				<ul>
					<li><a href="http://localhost:8080/lodview/en__sentence1.ttl">en__sentence1.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence2.ttl">en__sentence2.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence3.ttl">en__sentence3.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence4.ttl">en__sentence4.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence5.ttl">en__sentence5.ttl</a></li>
				</ul>
				<i>translated (english->italian->english)</i>
				<ul>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence1.ttl">en_it_en__sentence1.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence2.ttl">en_it_en__sentence2.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence3.ttl">en_it_en__sentence3.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence4.ttl">en_it_en__sentence4.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence5.ttl">en_it_en__sentence5.ttl</a></li>
				</ul>
				<br>
				<b>outputs</b>: the example results of the comparison between pairs of ontologies
				<ul>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence1.ttl">en_VS_en_it_en__sentence1.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence2.ttl">en_VS_en_it_en__sentence2.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence3.ttl">en_VS_en_it_en__sentence3.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence4.ttl">en_VS_en_it_en__sentence4.ttl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence5.ttl">en_VS_en_it_en__sentence5.ttl</a></li>
				</ul>

				To access resources defined within a certain ontology, simply type http://localhost:8080/lodview/<a text-color="red">namespace-name</a><a text-color="green">/resource-name</a> where <i>namespace-name</i> is the ontology (see above the available ones) and <i>resource-name</i> is the IRI of the resource, stripped of its prefix.

				Some examples:
				<ul>
					<li><a href="http://localhost:8080/lodview/vocabulary.ttl/Expression">Expression</a> (defined within <i>vocabulary.ttl)</i></li>
					<li><a href="http://localhost:8080/lodview/output.ttl/expression_1">expression_1</a> (defined within <i>output.ttl)</i></li>
					<li><a href="http://localhost:8080/lodview/vocabulary.ttl/Expression">Expression</a> (defined within <i>vocabulary.ttl)</i></li>
				</ul>
			</div>

		</div>

		<div id="inverses" class="empty"></div> 
		<jsp:include page="inc/custom_footer.jsp"></jsp:include>
	</article>
	<jsp:include page="inc/footer.jsp"></jsp:include>

</body>
</html>
